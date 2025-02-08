# method-project

<pre>
  <code>
    <!--  Build and start the Docker services -->
    docker-compose up --build

    <!-- Add a new route -->
    curl -i -X POST "http://127.0.0.1:7887/routes" \
         -H "Content-Type: application/json" \
         -d '{"route": ["SEA", "SFO"]}'

    <!--  Retrieve routes  -->
    curl -i -X GET "http://127.0.0.1:7887/routes?start=SEA&end=AUS"

    <!--  Delete all routes -->
    curl -i -X DELETE "http://127.0.0.1:7887/routes"
  </code>
</pre>


Our current algorithm employs Breadth-First Search (BFS) with a time complexity of O(V + E). V represents vertices and E denotes edges. For weighted graphs, optimizing pathfinding with Dijkstra's or A* algorithms is advisable. Weighted could be determined factors like distance and difficulty of the route.

To enhance scalability, we've integrated Redis for in-memory data management, offering efficient data retrieval and storage to handle increased loads.

If this was with a large dataset/in production we plan to transition from SQLAlchemy to a database solution optimized for large-scale applications. Given our data's structured nature and the need for complex queries, we favor SQL databases over NoSQL for their ACID compliance and robust relational capabilities, ensuring data integrity and supporting sophisticated querying essential for our application's performance and reliability.
