# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase

from powtoon.models import Powtoon


ADMIN_USER = {"username": "test_admin", "password": "Test1234"}
TEST_USER1 = {"username": "test_user1", "password": "Test1234"}
TEST_USER2 = {"username": "test_user2", "password": "Test1234"}

VIEW_OR_CREATE_URL = '/powtoons/'
DETAIL_URL = VIEW_OR_CREATE_URL + "{obj_id}/"
SHARE_URL = VIEW_OR_CREATE_URL + "{obj_id}/share/"
SHARED_POWTOONS_URL = '/shared_powtoons/'


class EmptyPowtoonAPITest(APITestCase):

    def setUp(self):
        self.username = TEST_USER1["username"]
        self.client.login(**TEST_USER1)
        self.data = {"name": "API powtoon", "content_json": {"dd": 2}}

    def test_empty_powtoon_list_api(self):
        response = self.client.get(VIEW_OR_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_view_powtoon_with_non_existing_id(self):
        non_existing = 1
        response = self.client.get(DETAIL_URL.format(obj_id=non_existing))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_powtoon_with_non_existing_id(self):
        non_existing = 1
        url = DETAIL_URL.format(obj_id=non_existing)
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_powtoon_with_non_existing_id(self):
        non_existing = 1
        url = DETAIL_URL.format(obj_id=non_existing)
        response = self.client.delete(url, data={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_powtoon_with_valid_data(self):
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        response = self.client.post(VIEW_OR_CREATE_URL, data=data, format="json")
        powtoons = Powtoon.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(powtoons.count(), 1)

    def test_get_powtoon_list(self):
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        self.client.post(VIEW_OR_CREATE_URL, data=data, format="json")

        response = self.client.get(VIEW_OR_CREATE_URL)
        powtoons = Powtoon.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(powtoons.count(), 1)

    def test_share_powtoon(self):
        data = {"name": "API powtoon", "content_json": {"dd": 2}}
        self.client.post(VIEW_OR_CREATE_URL, data=data, format="json")

        user2 = User.objects.get(username="test_user2")

        response = self.client.get(VIEW_OR_CREATE_URL)
        powtoon = Powtoon.objects.last()
        share_data = {"user_id": user2.pk}
        response = self.client.post(SHARE_URL.format(obj_id=powtoon.pk), data=share_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(list(Powtoon.objects.last().shared_with_users.all()), [user2])
        self.assertEqual(Group.objects.last().name, 'user_group_permission')

    def test_view_powtoon_with_valid_id(self):
        self.client.post(VIEW_OR_CREATE_URL, data=self.data, format="json")
        powtoon = Powtoon.objects.last()

        response = self.client.get(DETAIL_URL.format(obj_id=powtoon.pk))
        self.data["id"] = powtoon.pk
        self.data["owner"] = self.username
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.data)


class TestSharedPowtoonAPITest(APITestCase):
    def setUp(self):
        self.user2 = User.objects.get(username=TEST_USER2["username"])
        self.client.login(**TEST_USER1)
        self.data = {"name": "API powtoon", "content_json": {"data": 1}}
        response = self.client.post(VIEW_OR_CREATE_URL, data=self.data, format="json")
        assert 'id' in response.json(), response.json()
        self.powtoon_id = response.json()['id']
        self.view_detail_url = DETAIL_URL.format(obj_id=self.powtoon_id)
        self.share_data = {"user_id": self.user2.pk}
        self.client.logout()

    def test_view_shared_powtoon_detail(self):
        self.client.login(**TEST_USER1)
        share_url = SHARE_URL.format(obj_id=self.powtoon_id)
        response = self.client.post(share_url, data=self.share_data, format='json')
        self.client.logout()
        self.client.login(**TEST_USER2)

        r = self.client.get(VIEW_OR_CREATE_URL)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        url = DETAIL_URL.format(obj_id=self.powtoon_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.powtoon_id)

    def test_admin_view_not_own_powtoon(self):
        self.client.login(**ADMIN_USER)
        response = self.client.get(VIEW_OR_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_view_not_shared_and_not_own_powtoon(self):
        self.client.login(**ADMIN_USER)
        response = self.client.get(VIEW_OR_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_shared_powtoon(self):
        share_url = VIEW_OR_CREATE_URL + str(self.powtoon_id) + '/share/'
        self.client.post(share_url, data=self.share_data, format='json')
        self.client.login(**TEST_USER2)

        view_detail_url = VIEW_OR_CREATE_URL + str(self.powtoon_id) + "/"
        response = self.client.delete(view_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_shared_powtoon(self):

        share_url = VIEW_OR_CREATE_URL + str(self.powtoon_id) + '/share/'
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

    def setUp(self):
        self.user2 = User.objects.get(username="test_user2")
        self.client.login(**TEST_USER1)
        self.data = {"name": "API powtoon", "content_json": {"data": 1}}
        response = self.client.post(VIEW_OR_CREATE_URL, data=self.data, format="json")
        assert 'id' in response.json(), response.json()
        self.powtoon_id = response.json()['id']
        self.view_detail_url = VIEW_OR_CREATE_URL + str(self.powtoon_id) + "/"

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

    def test_get_shared_powtoons(self):
        response = self.client.get(SHARED_POWTOONS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
