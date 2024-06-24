
// type.action -> type.action
// chat.request -> chat.display
// inline_completion.accept -> completion.accepted
// explanation.request -> explanation.display
// docstring.request -> docstring.display
// bug_fixing.request -> bug_fix.request
// unit_tests.display -> unit_tests.display

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'chat',
        "data.action": 'request',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'chat',
            "data.action": 'display'
        }
    },
);

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'inline_completion',
        "data.action": 'accept',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'completion',
            "data.action": 'accepted'
        }
    },
);

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'explanation',
        "data.action": 'request',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'explanation',
            "data.action": 'display'
        }
    },
);

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'docstring',
        "data.action": 'request',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'docstring',
            "data.action": 'display'
        }
    },
);

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'bug_fixing',
        "data.action": 'request',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'bug_fix',
            "data.action": 'request'
        }
    },
);

use('memetrics');
db.getCollection('events').updateMany(
    {
        "data.app": "/osf/allai/vscode/OSFDigital.allai",
        "data.type": 'client:unit_tests',
        "data.action": 'display',
        schema_version: 0
    },
    {
        $set: {
            "data.type": 'unit_tests',
            "data.action": 'display'
        }
    },
);
