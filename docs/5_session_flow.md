In simple: Cookie = session key : session value

after register or login backend stores a session in database with 7 days of expiry. 

then when frontend fetch the backend router , backend stores a cookie with the session value from the database to authorize. 

in frontend credentials include