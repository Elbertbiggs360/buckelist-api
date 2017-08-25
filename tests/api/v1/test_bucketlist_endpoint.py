import json

from tests.base_test import BaseCase
from app.models.bucketlist import Bucketlist


class TestBucketlistEndpoint(BaseCase):
    ''' A class to test the bucketlist endpoints '''
    def setUp(self):
        super(TestBucketlistEndpoint, self).setUp()
        self.bucketlist_data = {'name': 'Eat Sushi'}

    def test_post_bucketlists_adds_new_bucketlist(self):
        with self.app.app_context():
            response = self.client().post(
                '/api/v1/bucketlists',
                data=json.dumps(self.bucketlist_data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Bucketlist created successfully!',
                         json.loads(response.data.decode('utf-8')).get('message'))

    def test_get_returns_all_bucketlists_for_user(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/bucketlists')
            result = response.data
        self.assertEqual(response.status_code, 200)

    def test_get_returns_one_bucketlist_if_id_is_specified(self):
        with self.app.app_context():
            self.add_test_bucketlists()
            response = self.client().get('/api/v1/bucketlists/1')
        result = json.loads(response.data.decode('utf-8'))
        expected_list = sorted(['id', 'name', 'items', 'date_created', 'date_modified', 'created_by'])
        self.assertEqual(response.status_code, 200)
        self.assertListEqual([result.get('name'), result.get('created_by')], ['sample_1', 1])

    def test_edit_updates_bucketlist_fields(self):
        with self.app.app_context():
            self.add_test_bucketlists()
            response = self.client().get('/api/v1/bucketlists/1')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(result.get('name'), 'sample_1')

        update_fields = {'name': 'Bungee Jump'}
        with self.app.app_context():
            response = self.client().put('/api/v1/bucketlists/1', data=json.dumps(update_fields))
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('name'), update_fields.get('name'))

    def test_delete_removes_bucketlist_from_database(self):
        with self.app.app_context():
            self.add_test_bucketlists()

            self.assertEqual(len(Bucketlist.query.all()), 4)

            response = self.client().delete('/api/v1/bucketlists/1')
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('message'), 'Bucketlist with ID#1 successfully deleted.')
        with self.app.app_context():
            self.assertEqual(len(Bucketlist.query.all()), 3)