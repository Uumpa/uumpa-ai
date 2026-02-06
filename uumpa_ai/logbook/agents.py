import uuid
import secrets
import functools


from . import forgejo
from .. import config


AGENT_TASK_LABEL = 'agent-task'
PENDING_AGENT_TASK_LABEL = 'pending-agent-task'


def create_agent_user():
    basename = uuid.uuid4().hex
    name = f"{config.FORGEJO_AGENT_USER_PREFIX}_{basename}"
    email = config.FORGEJO_AGENT_USER_EMAIL_TEMPLATE.format(basename=basename)
    forgejo.post("/admin/users", json={
        'email': email,
        'username': name,
        'password': secrets.token_urlsafe(20),
        'must_change_password': False,
        'restricted': False,
    })
    forgejo.put(f"/teams/{agents_team_id()}/members/{name}")
    return name


@functools.lru_cache(maxsize=None)
def agents_team_id():
    teams = forgejo.get(f'/orgs/{config.FORGEJO_LOGBOOK_ORG_NAME}/teams/search?q=agents')
    assert teams and len(teams['data']) == 1, 'Logbook agents team not found'
    return teams['data'][0]['id']
