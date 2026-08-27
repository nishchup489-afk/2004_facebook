from pydantic import BaseModel


class FriendSummary(BaseModel):

    user_id: int

    first_name: str

    last_name: str

    profile_pic: str | None

    university_name: str

    status: str | None

    username: str | None

    looking_for: str | None = None

    relationship_status: str | None = None

    friendship_status: str = "none"


class FriendSuggestion(FriendSummary):

    mutual_friend_count: int

    suggestion_reason: str


class FriendshipStatusResponse(BaseModel):

    status: str


class FriendActionResponse(BaseModel):

    status: str

    message: str


class FriendsResponse(BaseModel):

    friends: list[FriendSummary]

    count: int


class FriendRequestsResponse(BaseModel):

    requests: list[FriendSummary]

    count: int


class FriendSuggestionsResponse(BaseModel):

    suggestions: list[FriendSuggestion]

    count: int


class MutualFriendsResponse(BaseModel):

    friends: list[FriendSummary]

    count: int
