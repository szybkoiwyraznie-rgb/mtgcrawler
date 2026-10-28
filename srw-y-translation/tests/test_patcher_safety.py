import sys
from pathlib import Path

import tree_sitter
import tree_sitter_powershell

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_patcher import PS1


def test_powershell_parser():
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_powershell.language()))
    tree = parser.parse(PS1.replace('@@AA@@', 'aa').replace('@@GAME@@', 'game').encode())
    assert not tree.root_node.has_error


def test_install_checks_payload_backup_and_temporary_before_replacement():
    install = PS1.split('function Install-All', 1)[1].split('function Check-All', 1)[0]
    replace = install.index('Move-Item -LiteralPath $temp -Destination $target -Force')
    for check in ('(Hash-Of $source) -ne $patched', '(Hash-Of $backup) -ne $original',
                  '(Hash-Of $temp) -ne $patched'):
        assert install.index(check) < replace
    assert 'Copy-Item -LiteralPath $target -Destination $backup -Force' not in install


def test_restore_checks_backup_target_and_temporary_before_replacement():
    revert = PS1.split('function Revert-All', 1)[1].split('# ---------------------------------------------------------------- start', 1)[0]
    replace = revert.index('Move-Item -LiteralPath $temp -Destination $target -Force')
    for check in ('(Hash-Of $backup) -ne $row.Original', '$current -ne $row.Patched',
                  '(Hash-Of $temp) -ne $row.Original'):
        assert revert.index(check) < replace
