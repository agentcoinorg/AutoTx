create table "public"."task_errors" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "message" text not null,
    "task_id" uuid not null,
    "app_user_id" uuid not null,
    "app_id" uuid not null,
    "context" text not null
);


alter table "public"."task_errors" enable row level security;

alter table "public"."tasks" add column "logs" json;

CREATE UNIQUE INDEX task_errors_pkey ON public.task_errors USING btree (id);

alter table "public"."task_errors" add constraint "task_errors_pkey" PRIMARY KEY using index "task_errors_pkey";

alter table "public"."task_errors" add constraint "public_task_errors_app_id_fkey" FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE not valid;

alter table "public"."task_errors" validate constraint "public_task_errors_app_id_fkey";

alter table "public"."task_errors" add constraint "public_task_errors_app_user_id_fkey" FOREIGN KEY (app_user_id) REFERENCES app_users(id) ON DELETE CASCADE not valid;

alter table "public"."task_errors" validate constraint "public_task_errors_app_user_id_fkey";

alter table "public"."task_errors" add constraint "public_task_errors_task_id_fkey" FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE not valid;

alter table "public"."task_errors" validate constraint "public_task_errors_task_id_fkey";

grant delete on table "public"."task_errors" to "anon";

grant insert on table "public"."task_errors" to "anon";

grant references on table "public"."task_errors" to "anon";

grant select on table "public"."task_errors" to "anon";

grant trigger on table "public"."task_errors" to "anon";

grant truncate on table "public"."task_errors" to "anon";

grant update on table "public"."task_errors" to "anon";

grant delete on table "public"."task_errors" to "authenticated";

grant insert on table "public"."task_errors" to "authenticated";

grant references on table "public"."task_errors" to "authenticated";

grant select on table "public"."task_errors" to "authenticated";

grant trigger on table "public"."task_errors" to "authenticated";

grant truncate on table "public"."task_errors" to "authenticated";

grant update on table "public"."task_errors" to "authenticated";

grant delete on table "public"."task_errors" to "service_role";

grant insert on table "public"."task_errors" to "service_role";

grant references on table "public"."task_errors" to "service_role";

grant select on table "public"."task_errors" to "service_role";

grant trigger on table "public"."task_errors" to "service_role";

grant truncate on table "public"."task_errors" to "service_role";

grant update on table "public"."task_errors" to "service_role";


