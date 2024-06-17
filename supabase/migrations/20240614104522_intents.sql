delete from "public"."submitted_batches";
alter table "public"."submitted_batches" add column "transactions" json not null;

delete from "public"."tasks";
alter table "public"."tasks" drop column "transactions";
alter table "public"."tasks" add column "intents" json not null;


