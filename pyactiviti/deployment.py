
class Deployment:

    def deployments_url(self, *args):
        return self._to_endpoint('repository', 'deployments', *args)

    def deployment_url(self, deployment_id):
        return self.deployments_url(deployment_id)

    def deployments(self, **parameters):
        try:
            return self.rest_connection.get(self.deployments_url(),
                                            params=parameters)
        except ResponseError:
            raise NotImplementedError()

    def get_deployment(self, deployment_id):
        try:
            return self.rest_connection.get(self.deployment_url(deployment_id))
        except ResponseError as e:
            if e.status_code == codes.not_found:
                raise DeploymentNotFound()
            raise NotImplementedError()
