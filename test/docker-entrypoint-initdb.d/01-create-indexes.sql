BEGIN;

CREATE TABLE towns_index
(
  id serial,
  code character varying(10) NOT NULL,
  article text,
  name text NOT NULL,
  department character varying(4) NOT NULL,
  CONSTRAINT towns_index_pk PRIMARY KEY (id),
  CONSTRAINT towns_department_fkey FOREIGN KEY (department)
      REFERENCES public.departments (code) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE INDEX towns_index_article_index
  ON public.towns_index
  USING btree
  (article);

CREATE INDEX towns_index_article_name_index
  ON public.towns_index
  USING btree
  (article, name);

COMMIT;
