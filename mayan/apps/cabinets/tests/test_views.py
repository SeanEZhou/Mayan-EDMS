from __future__ import absolute_import, unicode_literals

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Cabinet
from ..permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document, permission_cabinet_view
)
from .literals import TEST_CABINET_LABEL, TEST_CABINET_EDITED_LABEL
from .mixins import CabinetTestMixin


class CabinetViewTestCase(CabinetTestMixin, GenericViewTestCase):
    def _request_create_cabinet(self, label):
        return self.post(
            'cabinets:cabinet_create', data={
                'label': TEST_CABINET_LABEL
            }
        )

    def test_cabinet_create_view_no_permission(self):
        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)
        self.assertEquals(response.status_code, 403)

        self.assertEqual(Cabinet.objects.count(), 0)

    def test_cabinet_create_view_with_permission(self):
        self.grant_permission(permission=permission_cabinet_create)

        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().label, TEST_CABINET_LABEL)

    def test_cabinet_create_duplicate_view_with_permission(self):
        self._create_test_cabinet()
        self.grant_permission(permission=permission_cabinet_create)

        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)
        # HTTP 200 with error message
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().pk, self.test_cabinet.pk)

    def _request_delete_cabinet(self):
        return self.post(
            viewname='cabinets:cabinet_delete', kwargs={
                'pk': self.test_cabinet.pk
            }
        )

    def test_cabinet_delete_view_no_permission(self):
        self._create_test_cabinet()

        response = self._request_delete_cabinet()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Cabinet.objects.count(), 1)

    def test_cabinet_delete_view_with_access(self):
        self._create_test_cabinet()
        self.grant_access(obj=self.test_cabinet, permission=permission_cabinet_delete)

        response = self._request_delete_cabinet()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Cabinet.objects.count(), 0)

    def _request_edit_cabinet(self):
        return self.post(
            viewname='cabinets:cabinet_edit', kwargs={
                'pk': self.test_cabinet.pk
            }, data={
                'label': TEST_CABINET_EDITED_LABEL
            }
        )

    def test_cabinet_edit_view_no_permission(self):
        self._create_test_cabinet()

        response = self._request_edit_cabinet()
        self.assertEqual(response.status_code, 403)

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.label, TEST_CABINET_LABEL)

    def test_cabinet_edit_view_with_access(self):
        self._create_test_cabinet()

        self.grant_access(obj=self.test_cabinet, permission=permission_cabinet_edit)

        response = self._request_edit_cabinet()
        self.assertEqual(response.status_code, 302)

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.label, TEST_CABINET_EDITED_LABEL)


class CabinetDocumentViewTestCase(CabinetTestMixin, GenericDocumentViewTestCase):
    def _add_document_to_cabinet(self):
        return self.post(
            viewname='cabinets:document_cabinet_add', kwargs={
                'pk': self.test_document.pk
            }, data={
                'cabinets': self.test_cabinet.pk
            }
        )

    def test_cabinet_add_document_view_no_permission(self):
        self._create_test_cabinet()

        self.grant_permission(permission=permission_cabinet_view)

        response = self._add_document_to_cabinet()
        self.assertContains(
            response=response, text='Select a valid choice.', status_code=200
        )

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 0)

    def test_cabinet_add_document_view_with_access(self):
        self._create_test_cabinet()

        self.grant_access(obj=self.test_cabinet, permission=permission_cabinet_view)
        self.grant_access(
            obj=self.test_cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.test_document, permission=permission_cabinet_add_document
        )

        response = self._add_document_to_cabinet()
        self.assertEqual(response.status_code, 302)

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.test_cabinet.documents.all(), (repr(self.test_document),)
        )

    def _request_add_multiple_documents_to_cabinet(self):
        return self.post(
            viewname='cabinets:document_multiple_cabinet_add', data={
                'id_list': (self.test_document.pk,), 'cabinets': self.test_cabinet.pk
            }
        )

    def test_cabinet_add_multiple_documents_view_no_permission(self):
        self._create_test_cabinet()

        self.grant_permission(permission=permission_cabinet_view)

        response = self._request_add_multiple_documents_to_cabinet()
        self.assertContains(
            response=response, text='Select a valid choice', status_code=200
        )

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 0)

    def test_cabinet_add_multiple_documents_view_with_access(self):
        self._create_test_cabinet()

        self.grant_access(
            obj=self.test_cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.test_document, permission=permission_cabinet_add_document
        )

        response = self._request_add_multiple_documents_to_cabinet()
        self.assertEqual(response.status_code, 302)

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.test_cabinet.documents.all(), (repr(self.test_document),)
        )

    def _request_remove_document_from_cabinet(self):
        return self.post(
            viewname='cabinets:document_cabinet_remove', kwargs={
                'pk': self.test_document.pk
            }, data={
                'cabinets': (self.test_cabinet.pk,),
            }
        )

    def test_cabinet_remove_document_view_no_permission(self):
        self._create_test_cabinet()

        self.test_cabinet.documents.add(self.test_document)

        response = self._request_remove_document_from_cabinet()
        self.assertContains(
            response=response, text='Select a valid choice', status_code=200
        )

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 1)

    def test_cabinet_remove_document_view_with_access(self):
        self._create_test_cabinet()

        self.test_cabinet.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_cabinet, permission=permission_cabinet_remove_document
        )
        self.grant_access(
            obj=self.test_document, permission=permission_cabinet_remove_document
        )

        response = self._request_remove_document_from_cabinet()
        self.assertEqual(response.status_code, 302)

        self.test_cabinet.refresh_from_db()
        self.assertEqual(self.test_cabinet.documents.count(), 0)

    def _request_cabinet_list(self):
        return self.get(viewname='cabinets:cabinet_list')

    def test_cabinet_list_view_no_permission(self):
        self._create_test_cabinet()

        response = self._request_cabinet_list()
        self.assertNotContains(
            response, text=self.test_cabinet.label, status_code=200
        )

    def test_cabinet_list_view_with_access(self):
        self._create_test_cabinet()
        self.grant_access(obj=self.test_cabinet, permission=permission_cabinet_view)

        response = self._request_cabinet_list()
        self.assertContains(
            response, text=self.test_cabinet.label, status_code=200
        )
