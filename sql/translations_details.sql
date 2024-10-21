CREATE TABLE IF NOT EXISTS public.translations_details
(
    uid uuid,
    hash text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.translations_details
    OWNER to postgres;
