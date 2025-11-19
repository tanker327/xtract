from xtract.models.post import Post, PostData
from xtract.models.user import UserDetails


def test_post_data_initialization():
    """Test PostData initialization with default values."""
    post_data = PostData()
    assert post_data.favorite_count == 0
    assert post_data.retweet_count == 0
    assert post_data.reply_count == 0
    assert post_data.quote_count == 0
    assert post_data.bookmark_count == 0
    assert post_data.is_quote_status is False
    assert post_data.lang == ""
    assert post_data.source == ""
    assert post_data.possibly_sensitive is False
    assert post_data.conversation_id == ""
    assert post_data.is_translatable is False
    assert post_data.grok_analysis_button is False


def test_post_data_from_dict():
    """Test PostData creation from dictionary."""
    tweet = {"source": "Twitter Web App", "is_translatable": True, "grok_analysis_button": True}
    legacy = {
        "favorite_count": 100,
        "retweet_count": 50,
        "reply_count": 25,
        "quote_count": 10,
        "bookmark_count": 5,
        "is_quote_status": True,
        "lang": "en",
        "possibly_sensitive": True,
        "conversation_id_str": "123456789",
    }

    post_data = PostData.from_dict(tweet, legacy)

    assert post_data.favorite_count == 100
    assert post_data.retweet_count == 50
    assert post_data.reply_count == 25
    assert post_data.quote_count == 10
    assert post_data.bookmark_count == 5
    assert post_data.is_quote_status is True
    assert post_data.lang == "en"
    assert post_data.source == "Twitter Web App"
    assert post_data.possibly_sensitive is True
    assert post_data.conversation_id == "123456789"
    assert post_data.is_translatable is True
    assert post_data.grok_analysis_button is True


def test_post_initialization():
    """Test Post initialization."""
    user_details = UserDetails(name="Test User", screen_name="testuser", followers_count=1000)

    post_data = PostData(favorite_count=50, retweet_count=20)

    post = Post(
        tweet_id="123456789",
        username="testuser",
        created_at="Wed Feb 28 12:00:00 +0000 2024",
        text="This is a test post",
        view_count="500",
        images=["https://example.com/image.jpg"],
        videos=[],
        user_details=user_details,
        post_data=post_data,
    )

    assert post.tweet_id == "123456789"
    assert post.username == "testuser"
    assert post.created_at == "Wed Feb 28 12:00:00 +0000 2024"
    assert post.text == "This is a test post"
    assert post.view_count == "500"
    assert len(post.images) == 1
    assert len(post.videos) == 0
    assert post.user_details.name == "Test User"
    assert post.user_details.followers_count == 1000
    assert post.post_data.favorite_count == 50
    assert post.post_data.retweet_count == 20
    assert post.quoted_tweet is None


def test_post_to_dict():
    """Test Post to_dict serialization."""
    user_details = UserDetails(name="Test User", screen_name="testuser", followers_count=1000)

    post_data = PostData(favorite_count=50, retweet_count=20)

    post = Post(
        tweet_id="123456789",
        username="testuser",
        created_at="Wed Feb 28 12:00:00 +0000 2024",
        text="This is a test post",
        view_count="500",
        images=["https://example.com/image.jpg"],
        videos=[],
        user_details=user_details,
        post_data=post_data,
    )

    post_dict = post.to_dict()

    assert post_dict["tweet_id"] == "123456789"
    assert post_dict["username"] == "testuser"
    assert post_dict["created_at"] == "Wed Feb 28 12:00:00 +0000 2024"
    assert post_dict["text"] == "This is a test post"
    assert post_dict["view_count"] == "500"
    assert len(post_dict["images"]) == 1
    assert len(post_dict["videos"]) == 0
    assert post_dict["user_details"]["name"] == "Test User"
    assert post_dict["user_details"]["followers_count"] == 1000
    assert post_dict["post_data"]["favorite_count"] == 50
    assert post_dict["post_data"]["retweet_count"] == 20
    assert "quoted_tweet" not in post_dict


def test_post_with_quoted_tweet():
    """Test Post with quoted tweet."""
    user_details = UserDetails(name="Test User", screen_name="testuser")

    post_data = PostData(favorite_count=50, retweet_count=20)

    quoted_user = UserDetails(name="Quoted User", screen_name="quoteduser")

    quoted_post_data = PostData(favorite_count=100, retweet_count=30)

    quoted_post = Post(
        tweet_id="987654321",
        username="quoteduser",
        created_at="Wed Feb 28 11:00:00 +0000 2024",
        text="This is a quoted post",
        view_count="1000",
        images=[],
        videos=["https://example.com/video.mp4"],
        user_details=quoted_user,
        post_data=quoted_post_data,
    )

    post = Post(
        tweet_id="123456789",
        username="testuser",
        created_at="Wed Feb 28 12:00:00 +0000 2024",
        text="This is a test post with quote",
        view_count="500",
        images=[],
        videos=[],
        user_details=user_details,
        post_data=post_data,
        quoted_tweet=quoted_post,
    )

    assert post.quoted_tweet is not None
    assert post.quoted_tweet.tweet_id == "987654321"
    assert post.quoted_tweet.username == "quoteduser"
    assert post.quoted_tweet.text == "This is a quoted post"

    post_dict = post.to_dict()
    assert "quoted_tweet" in post_dict
    assert post_dict["quoted_tweet"]["tweet_id"] == "987654321"
    assert post_dict["quoted_tweet"]["text"] == "This is a quoted post"
    assert len(post_dict["quoted_tweet"]["videos"]) == 1
