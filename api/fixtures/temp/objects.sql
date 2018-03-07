#creacion de la vista necesaria para el servicio specialists-list-messages
CREATE OR REPLACE VIEW specialist_message_list AS
SELECT
  m.id,
  u.photo,
  u.nick,
    max(m.created_at) AS date,
  q.title,
    count(1)          AS total,
  q.client_id       AS client,
  m.specialist_id as specialist
FROM api_message m
  JOIN api_query q
    ON m.query_id = q.id
  JOIN api_client c
    ON q.client_id = c.user_ptr_id
  JOIN api_user u
    ON c.user_ptr_id = u.id
WHERE m.viewed = 0
GROUP BY q.client_id
ORDER BY 4;
#tablas necesarias para el fixture test_getspecialistmessages: user,client,specialist,query,message,category,queryplansacquired,queryplans,saledetail,sale,contract,seller,clasification,address , contracttype
#=========================================================================