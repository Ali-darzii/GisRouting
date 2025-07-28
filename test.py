from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from shapely.geometry import LineString
from geoalchemy2.shape import from_shape
from src.models import GisModel
from src.utils.postgres import prepare_connection_string
from src.config import SETTING

DATABASE_URL = prepare_connection_string(
    SETTING.POSTGRE_HOST,
    SETTING.POSTGRE_PORT,
    SETTING.POSTGRE_USER,
    SETTING.POSTGRE_PASS,
    SETTING.POSTGRE_DB,
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def insert_data():
    session.execute(text("DELETE FROM edges_vertices_pgr;"))
    session.query(GisModel).delete()
    session.commit()

    blue_lines = [
            LineString([(0, 0), (1, 1)]),  
            LineString([(1, 1), (2, 2)]),  
            LineString([(2, 2), (3, 3)]),
            LineString([(3, 3), (4, 4)]),
            # onother blue
            LineString([(0, 0), (12, 12)]),
            LineString([(12, 12), (14, 14)]),
            LineString([(14, 14), (2,2)]),
            LineString([(2, 2), (3, 3)]),
    ]


    black_lines_1 = [
        LineString([(2, 2), (3, 3)]),  
        LineString([(3, 3), (4, 4)]), 
    ]


    black_lines_2 = [
        LineString([(0, 0), (-1, 1)]),   
        LineString([(-1, 1), (-2, 2)]),
        LineString([(-2, 2), (-3, 3)]), 
    ]

    for line in blue_lines:
        session.add(GisModel(
            color="#0000FF",
            geom=from_shape(line, srid=4326),
            cost=1,
            reverse_cost=1
        ))

    for line in black_lines_1 + black_lines_2:
        session.add(GisModel(
            color="#000000",
            geom=from_shape(line, srid=4326),
            cost=1,
            reverse_cost=1
        ))

    session.commit()

    session.execute(text("SELECT pgr_createTopology('edges', 0.00001, 'geom', 'id');"))
    session.commit()

    print("Success")


def check_data():
    start_node = session.execute(text("""
        SELECT id FROM edges_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(0, 0), 4326)
        LIMIT 1
    """)).scalar()

    end_node = session.execute(text("""
        SELECT id FROM edges_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(3, 3), 4326)
        LIMIT 1
    """)).scalar()


    short_result = session.execute(text(f"""
        SELECT 
            e.id,
            e.source,
            e.target,
            e.color,
            e.cost,
            e.reverse_cost,
            ST_AsGeoJSON(e.geom)::json AS geometry,
            dj.seq,
            dj.cost AS segment_cost,
            dj.agg_cost
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost, reverse_cost
             FROM edges
             WHERE color = ''#0000FF''',
            {start_node}, {end_node},
            directed := false
        ) AS dj
        JOIN edges e ON dj.edge = e.id
        ORDER BY dj.seq
    """)).fetchall()

    all_result = session.execute(text(f"""
    SELECT 
        e.id,
        e.source,
        e.target,
        e.color,
        e.cost,
        e.reverse_cost,
        ST_AsGeoJSON(e.geom)::json AS geometry,
        dj.seq,
        dj.cost AS segment_cost,
        dj.agg_cost
    FROM pgr_ksp(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE color = ''#0000FF''',
        {start_node}, {end_node}, 5 
    ) AS dj
    JOIN edges e ON dj.edge = e.id
    ORDER BY dj.path_id, dj.seq
""")).fetchall()

    route_segments = []
    for row in all_result:
        segment = {
            "type": "Feature",
            "properties": {
                "id": row.id,
                "source": row.source,
                "target": row.target,
                "color": row.color,
                "cost": row.cost,
                "reverse_cost": row.reverse_cost,
                "seq": row.seq,
                "segment_cost": row.segment_cost,
                "agg_cost": row.agg_cost
            },
            "geometry": row.geometry
        }
        route_segments.append(segment)
    print(route_segments)
check_data()
