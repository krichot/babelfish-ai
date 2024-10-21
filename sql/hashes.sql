CREATE TABLE IF NOT EXISTS public.hashes
(
    hash text COLLATE pg_catalog."default" NOT NULL,
    original text COLLATE pg_catalog."default",
    translated text COLLATE pg_catalog."default",
    lang_from character varying(5) COLLATE pg_catalog."default",
    lang_to character varying(5) COLLATE pg_catalog."default",
    CONSTRAINT hash_table_pkey PRIMARY KEY (hash)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hashes
    OWNER to postgres;
