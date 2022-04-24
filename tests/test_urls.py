from gitclone.urls import parse_url
from gitclone.exceptions import RepositoryFormatException


def test_url_failing_empty():
    try:
        res = parse_url("")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_working():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_with_feature_branch():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@feature/main"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_with_feature_branch_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@feature/main gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_git_extension():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.git gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_given_extension():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.git gitclone.test"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone.test"
    assert delimiter == "/"


def test_url_https_working_other_extension():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.other gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.other"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_other_extension_nodest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.other"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.other"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_branch():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@main gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_branch_nodest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@main"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_nodest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_failing_noscheme():
    try:
        res = parse_url("github.com/evyli/gitclone")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_multiple_slashes():
    try:
        res = parse_url("https://github.com/evyli//gitclone")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath1():
    try:
        res = parse_url("https://github.com/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath2():
    try:
        res = parse_url("https://github.com")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme():
    try:
        res = parse_url("github.com")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme_dest():
    try:
        res = parse_url("github.com dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme_dest_branch():
    try:
        res = parse_url("github.com@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_working():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_branch():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@main"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_branch_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@main dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "main"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_working_with_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_working_with_at_in_path():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli@gitclone.git"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli"
    assert branch == "gitclone.git"
    assert dest == "evyli"
    assert delimiter == ":"


def test_url_ssh_working_with_at_in_path_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli@gitclone.git dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli"
    assert branch == "gitclone.git"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_failing_with_at_in_path_dest_branch():
    try:
        res = parse_url("git@github.com:evyli@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_failing_with_at_in_path_dest_branch2():
    try:
        res = parse_url("git@github.com:evyli.com@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_with_at_in_path_dest_branch():
    try:
        res = parse_url("https://github.com/evyli@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_with_at_in_path_dest_branch2():
    try:
        res = parse_url("https://github.com/evyli.com@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_working_with_feature_branch():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@feature/main"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_feature_branch_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@feature/main dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "feature/main"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_failing_with_empty_branch():
    try:
        res = parse_url("git@github.com:evyli/gitclone.git@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_on_third_argument():
    try:
        res = parse_url("git@github.com:evyli/gitclone.git@main dest dest2")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_oauth_working():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://oauth-key@github.com/evyli/gitclone.git"
    )
    assert baseurl == "https://oauth-key@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_oauth_working_with_dest():
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://oauth-key@github.com/evyli/gitclone.git dest"
    )
    assert baseurl == "https://oauth-key@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "dest"
    assert delimiter == "/"


def test_url_oauth_failing_no_part_after_key():
    try:
        res = parse_url("https://oauth-key@/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_oauth_failing_no_part_before_key():
    try:
        res = parse_url("https://@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme():
    try:
        res = parse_url("https:/@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme22():
    try:
        res = parse_url("https:/github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme23():
    try:
        res = parse_url("https:github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme23():
    try:
        res = parse_url("https/github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme2():
    try:
        res = parse_url("https:@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme3():
    try:
        res = parse_url("https/@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme4():
    try:
        res = parse_url("https@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme5():
    try:
        res = parse_url("@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url():
    try:
        res = parse_url("@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url2():
    try:
        res = parse_url("@/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url3():
    try:
        res = parse_url("/@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url4():
    try:
        res = parse_url("/@/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url5():
    try:
        res = parse_url("@ dest")
        assert res is None
    except RepositoryFormatException:
        pass
