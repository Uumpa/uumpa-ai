from . import forgejo, agents
from .. import config


def init_repo_labels():
    existing_labels = {
        label['name']: label['id'] for label in
        forgejo.get_pagination_iterator(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/labels')
    }
    for label, color in {
        agents.AGENT_TASK_LABEL: 'FFA500',
        agents.PENDING_AGENT_TASK_LABEL: 'FFFF00',
    }.items():
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
