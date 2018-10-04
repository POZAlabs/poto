CREATE_STATUS = 200
RETRIEVE_STATUS = 200
DELETE_STATUS = 204


def check_status(response, status):
    if response['ResponseMetadata']['HTTPStatusCode'] == status:
        return response
    else:
        raise Exception("Something wrong")
