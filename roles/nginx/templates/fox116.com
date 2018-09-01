server {
    listen 80 default_server;
    return 444;
}

server {
    listen [::]:80;
    listen 80;
    server_name fox116.com www.fox116.com;
    rewrite ^(.*) https://$host$1 permanent;
}

server {
    listen [::]:80;
    listen 80;
    server_name api.fox116.com;
    rewrite ^(.*) https://$host$1 permanent;
}

server {
      listen 443 ssl;
      server_name api.fox116.com;

      ssl_certificate ssl/api.fox116.com.crt ;
      ssl_certificate_key ssl/api.fox116.com.key ;
      ssl_session_timeout 5m;
      ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
      ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
      ssl_prefer_server_ciphers on;


      location /static {
        root /home/zhuan16/project/autowriting-webapp/static ;
      }

      location / {
        proxy_redirect off;
        proxy_pass http://192.168.0.10:8888/;
    }

  access_log /home/zhuan16/nginx/logs/api_access.log ;
  error_log /home/zhuan16/nginx/logs/api_error.log ;

}



server {
  listen 443 ssl;

  # The host name to respond to
  server_name fox116.com www.fox116.com;

  ssl_certificate ssl/fox116.com.crt ;
  ssl_certificate_key ssl/fox116.com.key ;
  ssl_session_timeout 5m;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
  ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
  ssl_prefer_server_ciphers on;


  access_log /home/zhuan16/nginx/logs/access_log.log ;
  error_log /home/zhuan16/nginx/logs/error_log.log ;

  # Path for static files
  root /home/zhuan16/project/autowriting-web/dist;

  # Specify a charset
  charset utf-8;

  # Custom 404 page
  error_page 404 /404.html;

}
