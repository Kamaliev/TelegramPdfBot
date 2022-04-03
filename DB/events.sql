drop table events;
create table events(
    id integer primary key,
    time datetime,
    user_id integer not null,
    filename text,
    foreign key (user_id) references Users(id)
);
select * from events