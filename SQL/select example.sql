/*
SELECT id, cr_number, ad_type, title, description, issue_date, due_date, category, location, jdoc->>'agency' AS agency, created_at, updated_at
FROM public.contract_opportunities;
*/


SELECT 
    co.id, 
    co.cr_number, 
    co.ad_type, 
    co.title, 
    co.description, 
    co.issue_date, 
    co.due_date, 
    co.category, 
    co.location, 
    co.created_at,
    co.updated_at,
    fields.key AS field_name,
    fields.value AS field_value
FROM contract_opportunities co
CROSS JOIN LATERAL jsonb_each_text(co.jdoc) AS fields;
