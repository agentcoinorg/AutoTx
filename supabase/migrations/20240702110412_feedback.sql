alter table "public"."tasks" add column "feedback" text;

alter table "public"."tasks" add column "previous_task_id" uuid;

alter table "public"."tasks" add constraint "public_tasks_previous_task_id_fkey" FOREIGN KEY (previous_task_id) REFERENCES tasks(id) not valid;

alter table "public"."tasks" validate constraint "public_tasks_previous_task_id_fkey";


