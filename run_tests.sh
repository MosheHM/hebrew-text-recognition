#!/bin/bash

# Run tests using Docker Compose test configuration
docker-compose -f docker-compose.test.yml run --rm test

# Exit with the same status as the test command
exit $?
