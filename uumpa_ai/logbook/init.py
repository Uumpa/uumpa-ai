import time
import json
import subprocess
import sys

from . import forgejo, agents, common
from .. import config


LABEL_COLORS = {
    agents.AGENT_TASK_LABEL: 'FFA500',
    agents.PENDING_AGENT_TASK_LABEL: 'FFFF00',
    **{
        agents.AGENT_TASK_STATUS_LABEL_PREFIX + status: '00FF00'
        for status in agents.AGENT_TASK_STATUSES
        if status not in (agents.AGENT_TASK_STATUS_NEW, agents.AGENT_TASK_STATUS_DONE)
    },
    common.ORCHESTRATOR_TASK_LABEL: '0000FF',
}


def init_repo_labels():
    existing_labels = {
        label['name']: label['id'] for label in
        forgejo.get_pagination_iterator(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/labels')
    }
    for label, color in LABEL_COLORS.items():
        if label in existing_labels:
            forgejo.patch(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/labels/{existing_labels[label]}', json={
                'name': label,
                'color': color,
            })
        else:
            forgejo.post(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/labels', json={
                'name': label,
                'color': color,
            })


def init_repo():
    if not forgejo.get(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook'):
        forgejo.post(f'/orgs/{config.FORGEJO_LOGBOOK_ORG_NAME}/repos', json={'name': 'logbook'})
    init_repo_labels()


def init_org_teams():
    team_config = {
        'name': 'agents',
        'permission': 'write',
        'includes_all_repositories': True,
        'units': [
            'issues.write',
        ]
    }
    teams = forgejo.get(f'/orgs/{config.FORGEJO_LOGBOOK_ORG_NAME}/teams/search?q=agents')
    if not teams or len(teams['data']) != 1:
        forgejo.post(f'/orgs/{config.FORGEJO_LOGBOOK_ORG_NAME}/teams', json=team_config)
    else:
        team_id = teams['data'][0]['id']
        forgejo.patch(f'/teams/{team_id}', json=team_config)


def init_org():
    if not forgejo.get(f'/orgs/{config.FORGEJO_LOGBOOK_ORG_NAME}'):
        forgejo.post('/orgs', json={
            'username': config.FORGEJO_LOGBOOK_ORG_NAME,
            'visibility': 'private',
        })
    init_org_teams()


def init_local_development_instance():
    assert config.FORGEJO_LOCAL_DEVELOPMENT_INSTANCE
    port = config.FORGEJO_LOCAL_DEVELOPMENT_INSTANCE_HTTP_PORT
    p = subprocess.run([
        "docker", "container", "inspect", "uumpa-ai-local-forgejo",
    ], stdout=subprocess.PIPE)
    if p.returncode != 0 or json.loads(p.stdout)[0]['State']['Status'] != 'running':
        subprocess.call(["docker", "rm", "-f", "uumpa-ai-local-forgejo"])
        subprocess.check_call([
            "docker", "run", "--rm", "-d",
            "-p", f"127.0.0.1:{port}:3000",
            "--name", "uumpa-ai-local-forgejo",
            "-v", f"{config.FORGEJO_LOCAL_DEVELOPMENT_INSTANCE_DATA_PATH}:/data",
            "codeberg.org/forgejo/forgejo:14"
        ])
        time.sleep(5)
    if not config.FORGEJO_API_URL or not config.FORGEJO_ORCHESTRATOR_ADMIN_API_TOKEN:
        print("Started local Forgejo instance", file=sys.stderr)
        print(f"Complete the setup by visiting http://localhost:{port}", file=sys.stderr)
        print("Create an admin user and an API token for it, then set the following in `.env` at the repo root:", file=sys.stderr)
        print(f"\nFORGEJO_API_URL=http://localhost:{port}/api", file=sys.stderr)
        print("FORGEJO_ORCHESTRATOR_ADMIN_API_TOKEN=the_token_you_just_created", file=sys.stderr)
        print("re-run init once done", file=sys.stderr)
        exit(1)
