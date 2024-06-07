create table "public"."app_users" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "agent_address" text not null,
    "app_id" uuid not null,
    "agent_private_key" text not null,
    "user_id" text not null
);


alter table "public"."app_users" enable row level security;

create table "public"."apps" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "name" text not null,
    "api_key" text not null,
    "allowed" boolean not null
);


alter table "public"."apps" enable row level security;

create table "public"."submitted_batches" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "address" text not null,
    "chain_id" bigint not null,
    "app_user_id" uuid not null,
    "app_id" uuid not null,
    "task_id" uuid not null
);


alter table "public"."submitted_batches" enable row level security;

create table "public"."tasks" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "updated_at" timestamp with time zone not null default now(),
    "prompt" text not null,
    "address" text not null,
    "chain_id" bigint not null,
    "running" boolean not null,
    "messages" json not null,
    "transactions" json not null,
    "app_id" uuid not null,
    "app_user_id" uuid not null
);


alter table "public"."tasks" enable row level security;

CREATE UNIQUE INDEX app_users_id_key ON public.app_users USING btree (id);

CREATE UNIQUE INDEX app_users_pkey ON public.app_users USING btree (id);

CREATE UNIQUE INDEX apps_api_key_key ON public.apps USING btree (api_key);

CREATE UNIQUE INDEX apps_pkey ON public.apps USING btree (id);

CREATE UNIQUE INDEX submitted_batches_pkey ON public.submitted_batches USING btree (id);

CREATE UNIQUE INDEX tasks_pkey ON public.tasks USING btree (id);

alter table "public"."app_users" add constraint "app_users_pkey" PRIMARY KEY using index "app_users_pkey";

alter table "public"."apps" add constraint "apps_pkey" PRIMARY KEY using index "apps_pkey";

alter table "public"."submitted_batches" add constraint "submitted_batches_pkey" PRIMARY KEY using index "submitted_batches_pkey";

alter table "public"."tasks" add constraint "tasks_pkey" PRIMARY KEY using index "tasks_pkey";

alter table "public"."app_users" add constraint "app_users_id_key" UNIQUE using index "app_users_id_key";

alter table "public"."app_users" add constraint "public_app_users_app_id_fkey" FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE not valid;

alter table "public"."app_users" validate constraint "public_app_users_app_id_fkey";

alter table "public"."apps" add constraint "apps_api_key_key" UNIQUE using index "apps_api_key_key";

alter table "public"."submitted_batches" add constraint "public_submitted_batches_app_id_fkey" FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE not valid;

alter table "public"."submitted_batches" validate constraint "public_submitted_batches_app_id_fkey";

alter table "public"."submitted_batches" add constraint "public_submitted_batches_app_user_id_fkey" FOREIGN KEY (app_user_id) REFERENCES app_users(id) ON DELETE CASCADE not valid;

alter table "public"."submitted_batches" validate constraint "public_submitted_batches_app_user_id_fkey";

alter table "public"."submitted_batches" add constraint "public_submitted_batches_task_id_fkey" FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE not valid;

alter table "public"."submitted_batches" validate constraint "public_submitted_batches_task_id_fkey";

alter table "public"."tasks" add constraint "public_tasks_app_id_fkey" FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE not valid;

alter table "public"."tasks" validate constraint "public_tasks_app_id_fkey";

alter table "public"."tasks" add constraint "public_tasks_app_user_id_fkey" FOREIGN KEY (app_user_id) REFERENCES app_users(id) ON DELETE CASCADE not valid;

alter table "public"."tasks" validate constraint "public_tasks_app_user_id_fkey";

grant delete on table "public"."app_users" to "anon";

grant insert on table "public"."app_users" to "anon";

grant references on table "public"."app_users" to "anon";

grant select on table "public"."app_users" to "anon";

grant trigger on table "public"."app_users" to "anon";

grant truncate on table "public"."app_users" to "anon";

grant update on table "public"."app_users" to "anon";

grant delete on table "public"."app_users" to "authenticated";

grant insert on table "public"."app_users" to "authenticated";

grant references on table "public"."app_users" to "authenticated";

grant select on table "public"."app_users" to "authenticated";

grant trigger on table "public"."app_users" to "authenticated";

grant truncate on table "public"."app_users" to "authenticated";

grant update on table "public"."app_users" to "authenticated";

grant delete on table "public"."app_users" to "service_role";

grant insert on table "public"."app_users" to "service_role";

grant references on table "public"."app_users" to "service_role";

grant select on table "public"."app_users" to "service_role";

grant trigger on table "public"."app_users" to "service_role";

grant truncate on table "public"."app_users" to "service_role";

grant update on table "public"."app_users" to "service_role";

grant delete on table "public"."apps" to "anon";

grant insert on table "public"."apps" to "anon";

grant references on table "public"."apps" to "anon";

grant select on table "public"."apps" to "anon";

grant trigger on table "public"."apps" to "anon";

grant truncate on table "public"."apps" to "anon";

grant update on table "public"."apps" to "anon";

grant delete on table "public"."apps" to "authenticated";

grant insert on table "public"."apps" to "authenticated";

grant references on table "public"."apps" to "authenticated";

grant select on table "public"."apps" to "authenticated";

grant trigger on table "public"."apps" to "authenticated";

grant truncate on table "public"."apps" to "authenticated";

grant update on table "public"."apps" to "authenticated";

grant delete on table "public"."apps" to "service_role";

grant insert on table "public"."apps" to "service_role";

grant references on table "public"."apps" to "service_role";

grant select on table "public"."apps" to "service_role";

grant trigger on table "public"."apps" to "service_role";

grant truncate on table "public"."apps" to "service_role";

grant update on table "public"."apps" to "service_role";

grant delete on table "public"."submitted_batches" to "anon";

grant insert on table "public"."submitted_batches" to "anon";

grant references on table "public"."submitted_batches" to "anon";

grant select on table "public"."submitted_batches" to "anon";

grant trigger on table "public"."submitted_batches" to "anon";

grant truncate on table "public"."submitted_batches" to "anon";

grant update on table "public"."submitted_batches" to "anon";

grant delete on table "public"."submitted_batches" to "authenticated";

grant insert on table "public"."submitted_batches" to "authenticated";

grant references on table "public"."submitted_batches" to "authenticated";

grant select on table "public"."submitted_batches" to "authenticated";

grant trigger on table "public"."submitted_batches" to "authenticated";

grant truncate on table "public"."submitted_batches" to "authenticated";

grant update on table "public"."submitted_batches" to "authenticated";

grant delete on table "public"."submitted_batches" to "service_role";

grant insert on table "public"."submitted_batches" to "service_role";

grant references on table "public"."submitted_batches" to "service_role";

grant select on table "public"."submitted_batches" to "service_role";

grant trigger on table "public"."submitted_batches" to "service_role";

grant truncate on table "public"."submitted_batches" to "service_role";

grant update on table "public"."submitted_batches" to "service_role";

grant delete on table "public"."tasks" to "anon";

grant insert on table "public"."tasks" to "anon";

grant references on table "public"."tasks" to "anon";

grant select on table "public"."tasks" to "anon";

grant trigger on table "public"."tasks" to "anon";

grant truncate on table "public"."tasks" to "anon";

grant update on table "public"."tasks" to "anon";

grant delete on table "public"."tasks" to "authenticated";

grant insert on table "public"."tasks" to "authenticated";

grant references on table "public"."tasks" to "authenticated";

grant select on table "public"."tasks" to "authenticated";

grant trigger on table "public"."tasks" to "authenticated";

grant truncate on table "public"."tasks" to "authenticated";

grant update on table "public"."tasks" to "authenticated";

grant delete on table "public"."tasks" to "service_role";

grant insert on table "public"."tasks" to "service_role";

grant references on table "public"."tasks" to "service_role";

grant select on table "public"."tasks" to "service_role";

grant trigger on table "public"."tasks" to "service_role";

grant truncate on table "public"."tasks" to "service_role";

grant update on table "public"."tasks" to "service_role";


