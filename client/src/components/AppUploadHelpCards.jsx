import React from "react";
import { Card, ListGroup } from "react-bootstrap";

const AppUploadHelpCards = () => (
  <>
    <Card>
      <Card.Header>Common requirements</Card.Header>
      <Card.Body>
        <ListGroup variant="flush" className="mb-2">
          <ListGroup.Item>File size is less than 8MB</ListGroup.Item>
          <ListGroup.Item>
            Files <mark>requirements.txt</mark> and configuration{" "}
            <mark>env</mark> are required and should be located at the app root
          </ListGroup.Item>
          <ListGroup.Item>
            Module with WSGI application is required
          </ListGroup.Item>
          <ListGroup.Item>
            WSGI app instance inside module should be named as{" "}
            <mark>application</mark>
          </ListGroup.Item>
        </ListGroup>
      </Card.Body>
    </Card>
    <Card>
      <Card.Header>Configuration example</Card.Header>
      <Card.Body>
        <pre>
          <samp>
            ENTRYPOINT=bikes.wsgi     # required
            <br />
            PROJECT_WORKDIR=bikes     # project root if exists
            <br />
            STATIC_PATH=bikes/static/         # path to static files
            <br />
            APP_NAME=T100
            <br />
            APP_DESCRIPTION=Hacks internet
            <br />
            DB_PORT=6345              # required if create db option is chosen
            <br />
            DB_USER=user              # required if create db option is chosen
            <br />
            DB_PASSWORD=pass          # required if create db option is chosen
            <br />
            DJANGO_SETTINGS_MODULE=bikes.settings     # app specific settings
          </samp>
        </pre>
      </Card.Body>
    </Card>
  </>
);

export default AppUploadHelpCards;
