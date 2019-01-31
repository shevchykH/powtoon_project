# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase

from powtoon.models import Powtoon


ADMIN_USER = {"username": "test_admin", "password": "Test1234"}
TEST_USER2 = {"username": "test_user2", "password": "Test1234"}


class EmptyPowtoonAPITest(APITestCase):

    def setUp(self):
        self.username = "test_user1"
        self.client.login(username=self.username, password="Test1234")
        self.data = {"name": "API powtoon", "content_json": {"dd": 2}}

    def test_empty_powtoon_list_api(self):
        response = self.client.get('/powtoons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_view_powtoon_with_non_existing_id(self):
        invalid_id = 1
        response = self.client.get('/powtoons/{_id}/'.format(_id=invalid_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_powtoon_with_non_existing_id(self):
        invalid_id = 1
        url = '/powtoons/{_id}/'.format(_id=invalid_id)
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_powtoon_with_non_existing_id(self):
        invalid_id = 1
        url = '/powtoons/{_id}/'.format(_id=invalid_id)
        response = self.client.delete(url, data={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_powtoon_with_valid_data(self):
        url = '/powtoons/'
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        response = self.client.post(url, data=data, format="json")
        powtoons = Powtoon.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(powtoons.count(), 1)

    def test_get_powtoon_list(self):
        url = '/powtoons/'
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        self.client.post(url, data=data, format="json")

        response = self.client.get(url)
        powtoons = Powtoon.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(powtoons.count(), 1)

    def test_share_powtoon(self):
        url = '/powtoons/'
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        self.client.post(url, data=data, format="json")

        user2 = User.objects.get(username="test_user2")

        response = self.client.get(url)
        powtoon = Powtoon.objects.last()
        share_data = {"user_id": user2.pk}
        response = self.client.post(url + str(powtoon.pk) + "/share/", data=share_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(list(Powtoon.objects.last().shared_with_users.all()), [user2])
        self.assertEqual(Group.objects.last().name, 'user_group_permission')

    def test_view_powtoon_with_valid_id(self):
        url = '/powtoons/'

        self.client.post(url, data=self.data, format="json")

        powtoon = Powtoon.objects.last()

        response = self.client.get(url + str(powtoon.pk) + "/")
        self.data["id"] = powtoon.pk
        self.data["shared_with_users"] = []
        self.data["owner"] = self.username
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.data)


class TestSharedPowtoonAPITest(APITestCase):
    view_create_url = '/powtoons/'

    def setUp(self):
        self.user2 = User.objects.get(username="test_user2")
        self.client.login(username="test_user1", password="Test1234")
        self.data = {"name": "API powtoon", "content_json": {"data": 1}}
        response = self.client.post(self.view_create_url, data=self.data, format="json")
        assert 'id' in response.json(), response.json()
        self.powtoon_id = response.json()['id']
        self.view_detail_url = self.view_create_url + str(self.powtoon_id) + "/"
        self.share_data = {"user_id": self.user2.pk}
        self.client.logout()

    def test_view_shared_powtoon_detail(self):

        share_url = self.view_create_url + str(self.powtoon_id) + '/share/'
        response = self.client.post(share_url, data=self.share_data, format='json')
        self.client.login(username="test_user2", password="Test1234")

        r = self.client.get(self.view_create_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        url = self.view_create_url + str(self.powtoon_id) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.powtoon_id)

    def test_admin_view_not_own_powtoon(self):
        self.client.login(**ADMIN_USER)
        response = self.client.get(self.view_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_view_not_shared_and_not_own_powtoon(self):
        self.client.login(**ADMIN_USER)
        response = self.client.get(self.view_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_shared_powtoon(self):
        share_url = self.view_create_url + str(self.powtoon_id) + '/share/'
        self.client.post(share_url, data=self.share_data, format='json')
        self.client.login(**TEST_USER2)

        view_detail_url = self.view_create_url + str(self.powtoon_id) + "/"
        response = self.client.delete(view_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_shared_powtoon(self):

        share_url = self.view_create_url + str(self.powtoon_id) + '/share/'
        self.client.post(share_url, data=self.share_data, format='json')
        self.client.login(**TEST_USER2)

        data = deepcopy(self.data)
        data["name"] = "Updated Powtoon"
        data["content_json"] = {}
        response = self.client.put(self.view_detail_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Powtoon.objects.last().name, self.data["name"])
        self.assertEqual(Powtoon.objects.last().content_json, self.data["content_json"])


class TestUpdateDeletePowtoonAPITest(APITestCase):
    view_create_url = '/powtoons/'

    def setUp(self):
        self.user2 = User.objects.get(username="test_user2")
        self.client.login(username="test_user1", password="Test1234")
        self.data = {"name": "API powtoon", "content_json": {"data": 1}}
        response = self.client.post(self.view_create_url, data=self.data, format="json")
        assert 'id' in response.json(), response.json()
        self.powtoon_id = response.json()['id']
        self.view_detail_url = self.view_create_url + str(self.powtoon_id) + "/"

    def test_delete_own_powtoon(self):
        response = self.client.delete(self.view_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Powtoon.objects.count(), 0)

    def test_delete_not_own_powtoon(self):
        self.client.logout()
        self.client.login(**TEST_USER2)
        response = self.client.delete(self.view_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Powtoon.objects.count(), 1)

    def test_update_own_powtoon(self):
        data = deepcopy(self.data)
        data["name"] = "Updated Powtoon"
        data["content_json"] = {}
        response = self.client.put(self.view_detail_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Powtoon.objects.last().name, data["name"])
        self.assertEqual(Powtoon.objects.last().content_json, data["content_json"])
