"""Integration Tests — Events Domain

P0-B: Event lifecycle, RSVP, feed, validation, auth guards.
Uses product_user_a for event creation.
"""
import pytest
import requests
from datetime import datetime, timedelta
from tests.conftest import _next_test_ip, _make_headers, auth_header

pytestmark = pytest.mark.integration


def create_event(api_url, token, title='Test Event 4B', ip=None, **kwargs):
    h = auth_header(token, ip=ip or _next_test_ip())
    start = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    payload = {'title': title, 'startAt': start, 'category': 'SOCIAL', **kwargs}
    resp = requests.post(f'{api_url}/events', json=payload, headers=h)
    return resp, resp.json()


def rsvp_event(api_url, event_id, token, status='GOING', ip=None):
    h = auth_header(token, ip=ip or _next_test_ip())
    resp = requests.post(f'{api_url}/events/{event_id}/rsvp', json={'status': status}, headers=h)
    return resp, resp.json()


def cancel_rsvp(api_url, event_id, token, ip=None):
    h = auth_header(token, ip=ip or _next_test_ip())
    return requests.delete(f'{api_url}/events/{event_id}/rsvp', headers=h)


class TestCreateEvent:
    def test_create_event_success(self, api_url, product_user_a):
        resp, data = create_event(api_url, product_user_a['token'])
        assert resp.status_code == 201, f'Expected 201: {data}'
        event = data['event']
        assert event['title'] == 'Test Event 4B'
        assert event['category'] == 'SOCIAL'
        assert event['status'] == 'PUBLISHED'
        assert event['goingCount'] == 0

    def test_create_event_contract_shape(self, api_url, product_user_a):
        resp, data = create_event(api_url, product_user_a['token'], title='Shape check')
        assert resp.status_code == 201
        event = data['event']
        for field in ['id', 'creatorId', 'title', 'category', 'status', 'startAt',
                      'goingCount', 'interestedCount', 'createdAt']:
            assert field in event, f'Missing field: {field}'
        assert '_id' not in event

    def test_create_event_missing_title_rejected(self, api_url, product_user_a):
        h = auth_header(product_user_a['token'], ip=_next_test_ip())
        start = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        resp = requests.post(f'{api_url}/events', json={'startAt': start}, headers=h)
        assert resp.status_code == 400
        assert resp.json()['code'] == 'VALIDATION_ERROR'

    def test_create_event_invalid_category_rejected(self, api_url, product_user_a):
        resp, data = create_event(api_url, product_user_a['token'], title='Bad cat', category='INVALID')
        assert resp.status_code == 400
        assert data['code'] == 'VALIDATION_ERROR'

    def test_create_event_no_auth_blocked(self, api_url):
        h = _make_headers()
        start = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        resp = requests.post(f'{api_url}/events', json={'title': 'Fail', 'startAt': start}, headers=h)
        assert resp.status_code == 401


class TestGetEvent:
    def test_get_event_detail(self, api_url, product_user_a):
        _, created = create_event(api_url, product_user_a['token'], title='Detail test')
        event_id = created['event']['id']
        h = auth_header(product_user_a['token'], ip=_next_test_ip())
        resp = requests.get(f'{api_url}/events/{event_id}', headers=h)
        assert resp.status_code == 200
        assert resp.json()['event']['id'] == event_id

    def test_get_nonexistent_event_404(self, api_url, product_user_a):
        h = auth_header(product_user_a['token'], ip=_next_test_ip())
        resp = requests.get(f'{api_url}/events/fake-event-id', headers=h)
        assert resp.status_code == 404


class TestEventRSVP:
    def test_rsvp_going_success(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='RSVP test')
        event_id = created['event']['id']
        resp, data = rsvp_event(api_url, event_id, product_user_b['token'], 'GOING')
        assert resp.status_code == 200
        assert data['rsvp']['status'] == 'GOING'

    def test_rsvp_interested_success(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='Interested')
        event_id = created['event']['id']
        resp, data = rsvp_event(api_url, event_id, product_user_b['token'], 'INTERESTED')
        assert resp.status_code == 200
        assert data['rsvp']['status'] == 'INTERESTED'

    def test_rsvp_duplicate_idempotent(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='Dup RSVP')
        event_id = created['event']['id']
        rsvp_event(api_url, event_id, product_user_b['token'], 'GOING')
        resp, data = rsvp_event(api_url, event_id, product_user_b['token'], 'GOING')
        assert resp.status_code == 200
        assert data['rsvp']['status'] == 'GOING'

    def test_rsvp_invalid_status_rejected(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='Bad RSVP')
        event_id = created['event']['id']
        h = auth_header(product_user_b['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/rsvp', json={'status': 'MAYBE'}, headers=h)
        assert resp.status_code == 400

    def test_rsvp_nonexistent_event_404(self, api_url, product_user_b):
        resp, data = rsvp_event(api_url, 'fake-event-id', product_user_b['token'])
        assert resp.status_code == 404

    def test_cancel_rsvp_success(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='Cancel RSVP')
        event_id = created['event']['id']
        rsvp_event(api_url, event_id, product_user_b['token'], 'GOING')
        resp = cancel_rsvp(api_url, event_id, product_user_b['token'])
        assert resp.status_code == 200

    def test_cancel_rsvp_without_existing_404(self, api_url, product_user_a, product_user_b):
        _, created = create_event(api_url, product_user_a['token'], title='No RSVP cancel')
        event_id = created['event']['id']
        resp = cancel_rsvp(api_url, event_id, product_user_b['token'])
        assert resp.status_code == 404

    def test_rsvp_updates_count(self, api_url, product_user_a, product_user_b):
        """RSVP GOING should increment goingCount."""
        _, created = create_event(api_url, product_user_a['token'], title='Count RSVP')
        event_id = created['event']['id']
        resp, data = rsvp_event(api_url, event_id, product_user_b['token'], 'GOING')
        assert resp.status_code == 200
        assert data['rsvp']['goingCount'] >= 1

    def test_rsvp_no_auth_blocked(self, api_url, product_user_b):
        """Use product_user_b for event creation to avoid product_user_a's 10/hr limit."""
        resp, data = create_event(api_url, product_user_b['token'], title='Auth RSVP')
        assert resp.status_code == 201, f'Event creation failed: {data}'
        h = _make_headers()
        resp = requests.post(f'{api_url}/events/{data["event"]["id"]}/rsvp',
                             json={'status': 'GOING'}, headers=h)
        assert resp.status_code == 401


class TestEventFeed:
    def test_event_feed_requires_auth(self, api_url):
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/feed', headers=h)
        assert resp.status_code == 401

    def test_event_feed_returns_structure(self, api_url, product_user_a):
        h = auth_header(product_user_a['token'], ip=_next_test_ip())
        resp = requests.get(f'{api_url}/events/feed', headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert 'items' in data
        assert 'pagination' in data


class TestUpdateEvent:
    """PATCH /events/:id — edit event title/description/category."""

    def test_update_event_success(self, api_url, event_lifecycle_user):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='Before edit')
        event_id = created['event']['id']
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.patch(f'{api_url}/events/{event_id}',
                              json={'title': 'After edit'}, headers=h)
        assert resp.status_code == 200
        assert resp.json()['event']['title'] == 'After edit'

    def test_update_event_nonexistent_404(self, api_url, event_lifecycle_user):
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.patch(f'{api_url}/events/fake-event-id',
                              json={'title': 'Nope'}, headers=h)
        assert resp.status_code == 404

    def test_update_event_other_user_forbidden(self, api_url, event_lifecycle_user, product_user_b):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='Protected event')
        event_id = created['event']['id']
        h = auth_header(product_user_b['token'], ip=_next_test_ip())
        resp = requests.patch(f'{api_url}/events/{event_id}',
                              json={'title': 'Hijack'}, headers=h)
        assert resp.status_code == 403

    def test_update_cancelled_event_rejected(self, api_url, event_lifecycle_user, db):
        """Cannot edit a CANCELLED event."""
        _, created = create_event(api_url, event_lifecycle_user['token'], title='Will cancel')
        event_id = created['event']['id']
        db.events.update_one({'id': event_id}, {'$set': {'status': 'CANCELLED'}})
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.patch(f'{api_url}/events/{event_id}',
                              json={'title': 'Edit cancelled'}, headers=h)
        assert resp.status_code == 400


class TestDeleteEvent:
    """DELETE /events/:id — soft-delete (sets status=REMOVED)."""

    def test_delete_event_success(self, api_url, event_lifecycle_user):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='To delete')
        event_id = created['event']['id']
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.delete(f'{api_url}/events/{event_id}', headers=h)
        assert resp.status_code == 200
        assert resp.json()['message'] == 'Event removed'
        # Verify it returns 410
        resp2 = requests.get(f'{api_url}/events/{event_id}',
                             headers=auth_header(event_lifecycle_user['token'], ip=_next_test_ip()))
        assert resp2.status_code == 410

    def test_delete_event_nonexistent_404(self, api_url, event_lifecycle_user):
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.delete(f'{api_url}/events/fake-event-id', headers=h)
        assert resp.status_code == 404

    def test_delete_event_other_user_forbidden(self, api_url, event_lifecycle_user, product_user_b):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='No delete')
        event_id = created['event']['id']
        h = auth_header(product_user_b['token'], ip=_next_test_ip())
        resp = requests.delete(f'{api_url}/events/{event_id}', headers=h)
        assert resp.status_code == 403


class TestEventStateTransitions:
    """POST /events/:id/publish, /cancel, /archive — state machine."""

    def test_publish_draft_event(self, api_url, event_lifecycle_user):
        """Create as DRAFT, then publish → PUBLISHED."""
        _, created = create_event(api_url, event_lifecycle_user['token'],
                                  title='Draft to publish', isDraft=True)
        event_id = created['event']['id']
        assert created['event']['status'] == 'DRAFT'
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/publish', headers=h)
        assert resp.status_code == 200
        assert resp.json()['status'] == 'PUBLISHED'

    def test_publish_non_draft_rejected(self, api_url, event_lifecycle_user):
        """Already PUBLISHED → cannot publish again."""
        _, created = create_event(api_url, event_lifecycle_user['token'], title='Already pub')
        event_id = created['event']['id']
        assert created['event']['status'] == 'PUBLISHED'
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/publish', headers=h)
        assert resp.status_code == 400

    def test_cancel_event(self, api_url, event_lifecycle_user):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='To cancel')
        event_id = created['event']['id']
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/cancel',
                             json={'reason': 'Weather'}, headers=h)
        assert resp.status_code == 200
        assert resp.json()['message'] == 'Event cancelled'

    def test_cancel_already_cancelled_rejected(self, api_url, event_lifecycle_user, db):
        """Cannot cancel an already CANCELLED event."""
        _, created = create_event(api_url, event_lifecycle_user['token'], title='Double cancel')
        event_id = created['event']['id']
        db.events.update_one({'id': event_id}, {'$set': {'status': 'CANCELLED'}})
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/cancel', json={}, headers=h)
        assert resp.status_code == 400

    def test_archive_published_event(self, api_url, event_lifecycle_user):
        _, created = create_event(api_url, event_lifecycle_user['token'], title='To archive')
        event_id = created['event']['id']
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/archive', headers=h)
        assert resp.status_code == 200
        assert resp.json()['message'] == 'Event archived'

    def test_archive_draft_rejected(self, api_url, event_lifecycle_user, db):
        """Cannot archive a DRAFT event — use DB to set status instead of creating new event."""
        # Reuse an existing event by setting its status to DRAFT via DB
        event = db.events.find_one({'creatorId': event_lifecycle_user['userId'], 'status': {'$nin': ['REMOVED']}})
        assert event, 'Need an existing event to test archive-draft rejection'
        event_id = event['id']
        original_status = event['status']
        db.events.update_one({'id': event_id}, {'$set': {'status': 'DRAFT'}})
        h = auth_header(event_lifecycle_user['token'], ip=_next_test_ip())
        resp = requests.post(f'{api_url}/events/{event_id}/archive', headers=h)
        assert resp.status_code == 400
        # Restore original status
        db.events.update_one({'id': event_id}, {'$set': {'status': original_status}})


class TestEventSearch:
    """GET /events/search — public event search with filters."""

    def test_search_returns_structure(self, api_url):
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/search', headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert 'items' in data
        assert 'pagination' in data

    def test_search_by_query(self, api_url, event_lifecycle_user):
        """Search with q= param returns items."""
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/search?q=Test', headers=h)
        assert resp.status_code == 200
        assert 'items' in resp.json()

    def test_search_by_category_filter(self, api_url):
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/search?category=SOCIAL', headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert 'items' in data


class TestCollegeEventFeed:
    """GET /events/college/:id — college-scoped event feed."""

    def test_college_event_feed_returns_structure(self, api_url):
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/college/test-college-4b', headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert 'items' in data
        assert 'pagination' in data

    def test_college_event_feed_with_category(self, api_url):
        h = _make_headers()
        resp = requests.get(f'{api_url}/events/college/test-college-4b?category=SOCIAL', headers=h)
        assert resp.status_code == 200
        assert 'items' in resp.json()
