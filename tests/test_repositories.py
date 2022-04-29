from gitclone.exceptions import RepositoryFormatException
from gitclone.repositories import RepoSpecification


def parse_url(repostr: str) -> tuple[str, str, str, str, str, str]:
    return RepoSpecification.parse(repostr).extract()


def test_url_failing_empty() -> None:
    try:
        res = parse_url("")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_working() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_with_feature_branch() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@feature/main"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_with_feature_branch_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@feature/main gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_git_extension() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.git gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_given_extension() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.git gitclone.test"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone.test"
    assert delimiter == "/"


def test_url_https_working_other_extension() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.other gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.other"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_other_extension_nodest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone.other"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone.other"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_branch() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@main gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_branch_nodest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone@main"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_working_nodest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://github.com/evyli/gitclone"
    )
    assert baseurl == "https://github.com"
    assert path == "evyli/gitclone"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_https_failing_noscheme() -> None:
    try:
        res = parse_url("github.com/evyli/gitclone")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_multiple_slashes() -> None:
    try:
        res = parse_url("https://github.com/evyli//gitclone")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath1() -> None:
    try:
        res = parse_url("https://github.com/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath2() -> None:
    try:
        res = parse_url("https://github.com")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme() -> None:
    try:
        res = parse_url("github.com")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme_dest() -> None:
    try:
        res = parse_url("github.com dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_nopath_noscheme_dest_branch() -> None:
    try:
        res = parse_url("github.com@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_working() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_branch() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@main"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "main"
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_branch_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@main dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "main"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_working_with_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_working_with_at_in_path() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli@gitclone.git"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli"
    assert branch == "gitclone.git"
    assert dest == "evyli"
    assert delimiter == ":"


def test_url_ssh_working_with_at_in_path_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli@gitclone.git dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli"
    assert branch == "gitclone.git"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_failing_with_at_in_path_dest_branch() -> None:
    try:
        res = parse_url("git@github.com:evyli@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_failing_with_at_in_path_dest_branch2() -> None:
    try:
        res = parse_url("git@github.com:evyli.com@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_with_at_in_path_dest_branch() -> None:
    try:
        res = parse_url("https://github.com/evyli@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_https_failing_with_at_in_path_dest_branch2() -> None:
    try:
        res = parse_url("https://github.com/evyli.com@gitclone.git@main dest")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_ssh_working_with_feature_branch() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@feature/main"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "feature/main"
    assert dest == "gitclone"
    assert delimiter == ":"


def test_url_ssh_working_with_feature_branch_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "git@github.com:evyli/gitclone.git@feature/main dest"
    )
    assert baseurl == "git@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == "feature/main"
    assert dest == "dest"
    assert delimiter == ":"


def test_url_ssh_failing_with_empty_branch() -> None:
    try:
        res = parse_url("git@github.com:evyli/gitclone.git@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_on_third_argument() -> None:
    try:
        res = parse_url("git@github.com:evyli/gitclone.git@main dest dest2")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_oauth_working() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://oauth-key@github.com/evyli/gitclone.git"
    )
    assert baseurl == "https://oauth-key@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "gitclone"
    assert delimiter == "/"


def test_url_oauth_working_with_dest() -> None:
    baseurl, delimiter, path, _, branch, dest = parse_url(
        "https://oauth-key@github.com/evyli/gitclone.git dest"
    )
    assert baseurl == "https://oauth-key@github.com"
    assert path == "evyli/gitclone.git"
    assert branch == ""
    assert dest == "dest"
    assert delimiter == "/"


def test_url_oauth_failing_no_part_after_key() -> None:
    try:
        res = parse_url("https://oauth-key@/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_oauth_failing_no_part_before_key() -> None:
    try:
        res = parse_url("https://@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme() -> None:
    try:
        res = parse_url("https:/@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme22() -> None:
    try:
        res = parse_url("https:/github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme23() -> None:
    try:
        res = parse_url("https:github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme24() -> None:
    try:
        res = parse_url("https/github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme2() -> None:
    try:
        res = parse_url("https:@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme3() -> None:
    try:
        res = parse_url("https/@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme4() -> None:
    try:
        res = parse_url("https@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_scheme5() -> None:
    try:
        res = parse_url("@github.com/evyli/gitclone.git")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url() -> None:
    try:
        res = parse_url("@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url2() -> None:
    try:
        res = parse_url("@/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url3() -> None:
    try:
        res = parse_url("/@")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url4() -> None:
    try:
        res = parse_url("/@/")
        assert res is None
    except RepositoryFormatException:
        pass


def test_url_failing_invalid_url5() -> None:
    try:
        res = parse_url("@ dest")
        assert res is None
    except RepositoryFormatException:
        pass
