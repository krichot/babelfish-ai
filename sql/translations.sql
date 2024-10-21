CREATE TABLE IF NOT EXISTS public.translations
(
    uid uuid NOT NULL,
    title character(512) COLLATE pg_catalog."default",
    contents_original text COLLATE pg_catalog."default",
    contents_translated text COLLATE pg_catalog."default",
    status character(12) COLLATE pg_catalog."default",
    "timestamp" timestamp with time zone,
    CONSTRAINT translations_pkey PRIMARY KEY (uid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.translations
    OWNER to postgres;
