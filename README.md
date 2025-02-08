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
