from conftest import DEFAULT_VALID_PASSWORD
import pytest
from tasks.models import Task
from users.models import User


@pytest.mark.django_db
class TestAllTasksView():
    def test_not_authenticated_user_access_restricted(self, client, test_db):
        response = client.get('/tasks/')
        assert response.status_code == 200
        assert 'tasks' not in response.context.keys()

    @pytest.mark.parametrize('employee_flag', [(True), (False)],
                             ids=[
                                "employee",
                                "manager"
                             ])
    def test_authenticated_user_tasks_view(self, client, test_db, employee_flag):
        users = test_db[1] if employee_flag else test_db[2]
        assert len(users) > 0
        user = users[0]
        assert isinstance(user, User)
        client.login(username=user.user.username,
                     password=DEFAULT_VALID_PASSWORD)
        response = client.get('/tasks/', enforce_csrf_checks=True)
        assert response.status_code == 200
        assert 'tasks' in response.context.keys()
        assert all(isinstance(task, Task) for task in response.context['tasks'])
        assert len(response.context['tasks']) > 0
        if employee_flag:
            assert all(task.assignee == user for task in response.context['tasks'])
        else:
            assert all(task.assignee.team == user.team for task in response.context['tasks'])