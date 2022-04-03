drop table Users;
create table Users(
    id integer UNIQUE,
    first_name text,
    last_name text,
    date datetime

);
select *
from Users;