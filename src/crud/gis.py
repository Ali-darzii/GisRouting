from src.models.gis import GisModel
from shapely.geometry import Point
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.schema.gis import GisSchema, PropertiesSchema, GeometrySchema
from src.schema.gis import GisNode
class GisCrud:
    tolerance = 0.00000001

    def __init__(self, model: type[GisModel]) -> None:
        self.model = model

    def prepare_pgrout_network(self, db:Session):
        db.execute(text(f"""
                SELECT pgr_createTopology('edges', {self.tolerance}, 'geom', 'id');
            """))
        db.execute(text(f"""
                SELECT pgr_analyzeGraph('edges', {self.tolerance}, 'geom', 'id');
            """))
        db.commit()
    
    def finde_node(self, db:Session, lat:float, lng:float):
        return db.execute(text(
        f"""
        SELECT id FROM edges_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326)
        LIMIT 1
        """    
        )).scalar()
    
    def find_shortest_route_by_color(self, db: Session, gis_schema: GisSchema, color: str):
        start_node = self.finde_node(db, gis_schema.lng_source,gis_schema.lat_source)
        end_node = self.finde_node(db, gis_schema.lng_destination,gis_schema.lat_destination)
        queries = db.execute(text(
        f"""
        SELECT 
            e.id,e.source,e.target,e.color,e.cost,
            e.reverse_cost,ST_AsGeoJSON(e.geom)::json AS geometry,
            dj.seq,dj.cost AS segment_cost,dj.agg_cost
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost, reverse_cost
             FROM edges
             WHERE color = ''#0000FF''',
            {start_node}, {end_node},
            directed := false
        ) AS dj
        JOIN edges e ON dj.edge = e.id
        ORDER BY dj.seq
        """
        )).fetchall()
        result = []
        if queries:
            for row in queries:
                result.append(GisNode(
                    properties=PropertiesSchema(
                        id=row.id,
                        source=row.source,
                        target=row.target,
                        color=row.color,
                        cost=row.cost,
                        reverse_cost=row.reverse_cost,
                        seq=row.seq,
                        segment_cost=row.segment_cost,
                        agg_cost=row.agg_cost,
                    ),
                    geometry=GeometrySchema(
                        coordinates=row.geometry.get("coordinates")
                    )
                ))
        return result
    
    def find_best_5_route_by_color(self, db: Session, gis_schema: GisSchema, color: str):
        start_node = self.finde_node(db, gis_schema.lng_source, gis_schema.lat_source)
        end_node = self.finde_node(db, gis_schema.lng_destination, gis_schema.lat_destination)
        queries = db.execute(text(
        f"""
        SELECT 
            e.id,e.source,e.target,e.color,e.cost,
            e.reverse_cost,ST_AsGeoJSON(e.geom)::json AS geometry,dj.seq,
            dj.cost AS segment_cost,dj.agg_cost
        FROM pgr_ksp(
            'SELECT id, source, target, cost, reverse_cost FROM edges WHERE color = ''{color}''',
            {start_node}, {end_node}, 5
        ) AS dj
        JOIN edges e ON dj.edge = e.id
        ORDER BY dj.path_id, dj.seq
        """
        )).fetchall()
        result = []
        if queries:
            for row in queries:
                result.append(GisNode(
                    properties=PropertiesSchema(
                        id=row.id,
                        source=row.source,
                        target=row.target,
                        color=row.color,
                        cost=row.cost,
                        reverse_cost=row.reverse_cost,
                        seq=row.seq,
                        segment_cost=row.segment_cost,
                        agg_cost=row.agg_cost,
                    ),
                    geometry=GeometrySchema(
                        coordinates=row.geometry.get("coordinates")
                    )
                ))
        return result
            
        