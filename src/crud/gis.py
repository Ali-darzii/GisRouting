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
    
    def find_route(self, db, GisSchema: GisSchema, routing_algo='dijkstra'):
        """
        Find route between two points
        routing_algo can be: 'dijkstra', 'astar', 'bellman-ford'
        """
        
        # Find nearest nodes to source and target
        source_node = db.execute(text("""
            SELECT id FROM edges_vertices_pgr 
            ORDER BY the_geom <-> ST_SetSRID(ST_Point(:lng, :lat), 4326) LIMIT 1;
        """), {'lat': GisSchema.lat_source, 'lng': GisSchema.lng_source}).scalar()
        
        target_node = db.execute(text("""
            SELECT id FROM edges_vertices_pgr 
            ORDER BY the_geom <-> ST_SetSRID(ST_Point(:lng, :lat), 4326) LIMIT 1;
        """), {'lat': GisSchema.lat_destination, 'lng': GisSchema.lng}).scalar()
        
        if not source_node or not target_node:
            return None
            
        # Choose routing algorithm
        if routing_algo == 'dijkstra':
            query = """
                SELECT seq, node, edge, cost, agg_cost, geom 
                FROM pgr_dijkstra(
                    'SELECT id, source, target, cost, reverse_cost FROM edges',
                    :source, :target, directed := false
                ) JOIN edges ON edge = id;
            """
        elif routing_algo == 'astar':
            query = """
                SELECT seq, node, edge, cost, agg_cost, geom 
                FROM pgr_astar(
                    'SELECT id, source, target, cost, reverse_cost, x1, y1, x2, y2 FROM edges',
                    :source, :target, directed := false
                ) JOIN edges ON edge = id;
            """
        elif routing_algo == 'bellman-ford':
            query = """
                SELECT seq, node, edge, cost, agg_cost, geom 
                FROM pgr_bellmanford(
                    'SELECT id, source, target, cost, reverse_cost FROM edges',
                    :source, :target, directed := false
                ) JOIN edges ON edge = id;
            """
        else:
            raise ValueError("Invalid routing algorithm")
        
        # Execute routing query
        result = db.execute(text(query), {'source': source_node, 'target': target_node})
        route = result.fetchall()
        
        return route

