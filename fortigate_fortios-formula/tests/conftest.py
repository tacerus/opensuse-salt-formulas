"""
Pytest helper functions for testing the FortiGate FortiOS formula
Copyright (C) 2025 SUSE LLC <georg.pfuetzenreuter@suse.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from time import time
from lib import fg_exec, fg_ssh
from fabric import Connection
import pytest

def pytest_addoption(parser):
    parser.addoption('--target', action='store')

def pytest_generate_tests(metafunc):
    value = metafunc.config.option.target
    if 'target' in metafunc.fixturenames and value is not None:
        metafunc.parametrize('target', [value], scope='session')

@pytest.fixture(scope='session')
def device(target):
    # TODO: this should contain some semi random value
    backup_comment = f'PYTEST_PRE_{int(time())}'

    with fg_ssh(target) as conn:
        print()

        # create backup
        fg_exec(conn, f'execute backup config flash "{backup_comment}"')
        revision = None

        # get ID of backup created above (using sophisticated output parser)
        for backup in [{' '.join(l.split()[5:]): int(l.split()[0])} for l in fg_exec(conn, 'execute revision list config').splitlines() if l and l[0].isnumeric()]:
            for b_c, b_id in backup.items():
                if b_c == backup_comment:
                    revision = b_id
                    break

        if revision is None:
            raise RuntimeError

        yield target

        print()

        # restore backup
        # better would be some prompt/expect framework (since the FortiOS CLI seems to have 0 way to operate non-interactively or to do a yes-pipe), but I'm not sure how to implement it in Fabric
        # currently we assume the first prompt is always "Do you want to continue? (y/n)" => answer with "y"
        fg_exec(conn, f'execute restore config flash {revision}\ny')

        # maybe wait for device to reload here (will need to handle disconnection of SSH)?

        conn.close()

