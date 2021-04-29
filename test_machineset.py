import pytest


import json
import yaml
import uuid
import time

from kubernetes import client, config
from openshift.dynamic import DynamicClient


@pytest.fixture
def client():
    """ Fixture to set up openshift client. """
    k8s_client = config.new_client_from_config()
    return DynamicClient(k8s_client)


@pytest.fixture
def ms_resource(client):
    """ Helper fixture to get MachineSet resource from clien. t"""
    return client.resources.get(api_version='machine.openshift.io/v1beta1', kind='MachineSet')


def build_machineset(ms_resource):
    """ Helper fucntion to prepare MachineSet config. """
    print("PREPARING MACHINESET")
    machineset = ms_resource.get(
        namespace='openshift-machine-api').to_dict().get('items')[0]
    provider_spec = machineset.get("spec")["template"]["spec"]["providerSpec"]
    cluster_name = machineset.get(
        "metadata")["labels"]["machine.openshift.io/cluster-api-cluster"]
    namespace = "openshift-machine-api"
    uid = str(uuid.uuid4())
    replicas = 2

    labels = {
        "machine.openshift.io/cluster-api-cluster": cluster_name,
        "e2e.openshift.io": uid
    }

    body = {
        "apiVersion": "machine.openshift.io/v1beta1",
        "kind": "MachineSet",
        "metadata": {
            "labels": labels,
            "generateName": cluster_name,
            "namespace": namespace,
            "uid": uid
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": labels
            },
            "template": {
                "metadata": {
                    "labels": labels
                },
                "spec": {
                    "metadata": {},
                    "providerSpec": provider_spec
                }
            }
        }
    }

    return body, namespace


def machineset_running(client, namespace):
    """ Check if all machines from machineset are in running phase. """
    machines = client.resources.get(api_version='machine.openshift.io/v1beta1', kind='Machine').get(
        namespace='openshift-machine-api', label_selector='e2e.openshift.io').to_dict().get('items')
    try:
        for machine in machines:
            assert machine.get('status').get('phase') == 'Running'

        return True
    except:
        return False


def wait_for_machineset(client, namespace):
    """ Repeatedsly checks status of machines and times out ofter 15 mins. """
    print("WAITING FOR MACHINES TO BE READY")
    timeout = time.time() + 60*15   # 5 minutes from now
    while True:
        if machineset_running(client, namespace):
            print("ALL MACHINES FROM MACHINESET RUNNING")
            break
        elif time.time() > timeout:
            raise TimeoutError("TIMEOUT: MACHINESET MACHINES NOT RUNNING !")
        else:
            time.sleep(30)  # sleep 30 seconds


def delete_machineset(ms_resource, namespace):
    """ Deletes machineset resource and waits for its deletion. """
    ms_resource.delete(namespace=namespace, label_selector='e2e.openshift.io')

    timeout = time.time() + 60*15   # 5 minutes from now
    while True:
        deleted = len(ms_resource.get(namespace=namespace,
                      label_selector='e2e.openshift.io').to_dict().get('items')) == 0
        if deleted:
            print("ALL MACHINES FROM MACHINESET DELETED")
            break
        elif time.time() > timeout:
            raise TimeoutError(
                "TIMEOUT: MACHINESET MACHINES TOOK MORE THAN 15 MINUTES TO DELETE !")
        else:
            time.sleep(5)  # sleep 5 seconds


@pytest.fixture
def create_machineset(client, ms_resource):
    """ Fixture to create a machineset before each test and delete it after test. """
    body, namespace = build_machineset(ms_resource)
    print("CREATING A MACHINESET")
    ms_resource.create(body=body, namespace=namespace)
    wait_for_machineset(client, namespace)

    yield

    delete_machineset(ms_resource, namespace)


# TESTS
def test_one(client, ms_resource, create_machineset):
    """ Does nothing :) """
    ms_list_resource = ms_resource.get(
        namespace='openshift-machine-api', label_selector='e2e.openshift.io')

    ms = ms_list_resource.to_dict().get('items')[0]
    print("This test would do something. Sleeps for 15 seconds")
    time.sleep(15)
    print("MachineSet is running with " +
          str(ms.get("spec")["replicas"]) + " replicas.")


def test_two(client, ms_resource, create_machineset):
    """ Does nothing but longer :) """
    ms_list_resource = ms_resource.get(
        namespace='openshift-machine-api', label_selector='e2e.openshift.io')

    ms = ms_list_resource.to_dict().get('items')[0]
    print("This test would do something else :) Sleeps for 30 seconds. ")
    time.sleep(30)
    print("MachineSet is running with " + str(ms.get("spec")
          ["template"]["spec"]["providerSpec"]["value"]["kind"]))
