drop table if exists recipe;
create table recipe (
    id integer primary key autoincrement,
    name text not null,
    recipetypeid integer not null,
    instructions text not null
);

drop table if exists recipetype;
create table recipetype (
    id integer primary key autoincrement,
    name integer not null
);

drop table if exists ingredient;
create table ingredient (
    id integer primary key autoincrement,
    name integer not null,
    amazonid text,
    unittypeid integer not null,
    units real not null,
    price real,
    activeyn integer not null
);

drop table if exists ingpricehistory;
create table ingpricehistory (
    ingredientid integer,
    changedate date,
    fromprice real not null,
    toprice real not null,
    primary key (ingredientid, changedate)
);

drop table if exists recipeingmapping;
create table recipeingmapping (
    recipeid integer,
    ingredientid integer,
    unittypeid integer not null,
    units real not null,
    primary key (recipeid, ingredientid)
);

drop table if exists unittype;
create table unittype (
    id integer primary key autoincrement,
    name integer not null
);

-- theres a syntax error somewhere in here
-- drop table if exists order;
-- create table order (
--     id integer primary key autoincrement,
--     orderdate date not null,
--     status text not null
-- );

-- drop table if exists orderrecipes;
-- create table orderrecipes (
--     orderid integer,
--     recipeid integer,
--     voided date,
--     primary key (orderid, recipeid)
-- );