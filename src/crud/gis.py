from src.models.gis import GisModel
from shapely.geometry import Point
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.schema.gis import GisSchema

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
    
    def find_route(self, db:Session , gis_schema: GisSchema, color:str, routing_algo='dijkstra'):
        """
        Find route between two points
        routing_algo can be: 'dijkstra', 'astar', 'bellman-ford'
        """
        
        source_node = db.execute(text("""
            SELECT id FROM edges_vertices_pgr 
            ORDER BY the_geom <-> ST_SetSRID(ST_Point(:lng, :lat), 4326) LIMIT 1;
        """), {
            'lat': gis_schema.lat_source,
            'lng': gis_schema.lng_source
        }).scalar()
        
        target_node = db.execute(text("""
            SELECT id FROM edges_vertices_pgr 
            ORDER BY the_geom <-> ST_SetSRID(ST_Point(:lng, :lat), 4326) LIMIT 1;
        """), {
            'lat': gis_schema.lat_destination,
            'lng': gis_schema.lng_destination
        }).scalar()
        
        if not source_node or not target_node:
            return None

        edges_query = """
            SELECT id, source, target, cost, reverse_cost
            FROM edges
            WHERE color = :color
        """

        if routing_algo == 'dijkstra':
            query = text(f"""
                SELECT seq, node, edge, cost, agg_cost, geom, color 
                FROM pgr_dijkstra(
                    '{edges_query}',
                    :source, :target, directed := false
                ) JOIN edges ON edge = id;
            """)
        else:
            raise ValueError(f"Unsupported routing algorithm: {routing_algo}")

        result = db.execute(query, {
            'color': color,
            'source': source_node,
            'target': target_node
        })
        
        return result.fetchall()

