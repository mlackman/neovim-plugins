from ..jiraplugin import create_discussion, RawComment, Comment, create_raw_comments, render_discussion

COMMENTS = [{'self': 'https://prj.atlassian.net/rest/api/2/issue/46427/comment/48485', 'id': '48485', 'author': {'self': 'https://prj.atlassian.net/rest/api/2/user?accountId=5ee07715a1a84e0ab447cfec', 'accountId': '5ee07715a1a84e0ab447cfec', 'emailAddress': 'mika.lackman@younite.ai', 'avatarUrls': {'48x48': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/48', '24x24': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/24', '16x16': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/16', '32x32': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/32'}, 'displayName': 'Mika Lackman', 'active': True, 'timeZone': 'Etc/GMT', 'accountType': 'atlassian'}, 'body': '[~accountid:62259ecbf1e55c0070f0b4a5] question\nq', 'updateAuthor': {'self': 'https://prj.atlassian.net/rest/api/2/user?accountId=5ee07715a1a84e0ab447cfec', 'accountId': '5ee07715a1a84e0ab447cfec', 'emailAddress': 'mika.lackman@younite.ai', 'avatarUrls': {'48x48': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/48', '24x24': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/24', '16x16': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/16', '32x32': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/5ee07715a1a84e0ab447cfec/5b16e1a3-0d58-46a7-82c1-9cea4ce9b7f0/32'}, 'displayName': 'Mika Lackman', 'active': True, 'timeZone': 'Etc/GMT', 'accountType': 'atlassian'}, 'created': '2026-04-20T02:43:07.122+0000', 'updated': '2026-04-20T02:43:07.122+0000', 'jsdPublic': True}, {'self': 'https://prj.atlassian.net/rest/api/2/issue/46427/comment/48518', 'id': '48518', 'author': {'self': 'https://prj.atlassian.net/rest/api/2/user?accountId=62259ecbf1e55c0070f0b4a5', 'accountId': '62259ecbf1e55c0070f0b4a5', 'avatarUrls': {'48x48': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '24x24': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '16x16': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '32x32': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png'}, 'displayName': 'Petri Perä', 'active': True, 'timeZone': 'Etc/GMT', 'accountType': 'atlassian'}, 'body': '[~accountid:5ee07715a1a84e0ab447cfec] Answer', 'updateAuthor': {'self': 'https://prj.atlassian.net/rest/api/2/user?accountId=62259ecbf1e55c0070f0b4a5', 'accountId': '62259ecbf1e55c0070f0b4a5', 'avatarUrls': {'48x48': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '24x24': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '16x16': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png', '32x32': 'https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/NM-1.png'}, 'displayName': 'Petri Perä', 'active': True, 'timeZone': 'Etc/GMT', 'accountType': 'atlassian'}, 'created': '2026-04-20T03:59:00.097+0000', 'updated': '2026-04-20T03:59:00.097+0000', 'parentId': 48485, 'jsdPublic': True}]

def test_creating_raw_comment():
    comments = create_raw_comments(COMMENTS) 
    assert comments[0].id == '48485'
    assert comments[0].parent_id == None
    assert comments[0].author == 'Mika Lackman' 
    assert comments[0].body == '[~accountid:62259ecbf1e55c0070f0b4a5] question\nq' 

def test_real_data():
    comments = create_raw_comments(COMMENTS) 
    discussions = create_discussion(comments)

    assert len(discussions) == 1

    text = render_discussion(discussions[0])

    expected = "- [Mika Lackman]\n\n\t[~accountid:62259ecbf1e55c0070f0b4a5] question\n\tq\n\n\n\t- [Petri Perä]\n\n\t\t[~accountid:5ee07715a1a84e0ab447cfec] Answer\n\n\n"
    assert expected == text


def test_create_discussion_no_answers():
    comments = create_discussion([RawComment(id='1', parent_id=None, author='Darth Vader', body='Find that ship')])
    assert [Comment(author='Darth Vader', body='Find that ship', answers=[])] == comments


def test_create_discussion_with_threads():
    comments = create_discussion([
        RawComment(id='1', parent_id=None, author='Darth Vader', body='Luke, I`m your father!'),
        RawComment(id='2', parent_id='1', author='Luke Skywalker', body='Nooooooooo!!!!'),
        RawComment(id='3', parent_id=None, author='Han Solo', body='Nah, c`mon'),
    ])
    assert [
        Comment(
            author='Darth Vader', 
            body='Luke, I`m your father!', 
            answers=[
                Comment(author='Luke Skywalker', body='Nooooooooo!!!!', answers=[])
            ]
        ),
        Comment(
            author='Han Solo',
            body='Nah, c`mon',
            answers=[]
        )
        ] == comments


def test_create_discussion_with_answer():
    comments = create_discussion([
        RawComment(id='1', parent_id=None, author='Darth Vader', body='Luke, I`m your father!'),
        RawComment(id='2', parent_id='1', author='Luke Skywalker', body='Nooooooooo!!!!'),
    ])
    assert [
        Comment(
            author='Darth Vader', 
            body='Luke, I`m your father!', 
            answers=[
                Comment(author='Luke Skywalker', body='Nooooooooo!!!!', answers=[])
            ]
        )
        ] == comments


def test_create_discussion_with_answers():
    comments = create_discussion([
        RawComment(id='1', parent_id=None, author='Darth Vader', body='Luke, I`m your father!'),
        RawComment(id='2', parent_id='1', author='Luke Skywalker', body='Nooooooooo!!!!'),
        RawComment(id='3', parent_id='2', author='Darth Vader', body='Search your feelings!')

    ])
    assert [
        Comment(
            author='Darth Vader', 
            body='Luke, I`m your father!', 
            answers=[
                Comment(
                    author='Luke Skywalker', 
                    body='Nooooooooo!!!!', 
                    answers=[
                        Comment(author='Darth Vader', body='Search your feelings!', answers=[])
                    ]
                )
            ]
        )
        ] == comments
