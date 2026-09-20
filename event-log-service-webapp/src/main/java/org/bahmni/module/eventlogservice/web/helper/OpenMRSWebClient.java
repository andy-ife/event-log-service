package org.bahmni.module.eventlogservice.web.helper;

import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.security.cert.X509Certificate;


import org.bahmni.webclients.ConnectionDetails;
import org.bahmni.webclients.HttpClient;
import org.bahmni.webclients.openmrs.OpenMRSLoginAuthenticator;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.net.URI;

@Component
public class OpenMRSWebClient {

    protected HttpClient httpClient;
    protected ConnectionDetails connectionDetails;

    public String get(URI uri) {
        return httpClient.get(uri);
    }

    @Autowired
    public OpenMRSWebClient(OpenMRSProperties properties) {
        connectionDetails = connectionDetails(properties);
        httpClient = new HttpClient(connectionDetails, new OpenMRSLoginAuthenticator(connectionDetails));
    }

    private ConnectionDetails connectionDetails(OpenMRSProperties properties) {
        return new ConnectionDetails(properties.getOpenMRSAuthURL(),
                properties.getOpenMRSUser(),
                properties.getOpenMRSPassword(),
                properties.getConnectionTimeoutInMilliseconds(),
                properties.getReplyTimeoutInMilliseconds(),
                createTrustAllConnectionManager());
    }

    private PoolingHttpClientConnectionManager createTrustAllConnectionManager() {
        try {
            TrustManager[] trustAllCerts = new TrustManager[]{
                new X509TrustManager() {
                    public X509Certificate[] getAcceptedIssuers() { return null; }
                    public void checkClientTrusted(X509Certificate[] certs, String authType) { }
                    public void checkServerTrusted(X509Certificate[] certs, String authType) { }
                }
            };
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());
            SSLConnectionSocketFactory sslsf = new SSLConnectionSocketFactory(
                    sc, SSLConnectionSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER);
            Registry<ConnectionSocketFactory> registry = RegistryBuilder.<ConnectionSocketFactory>create()
                    .register("http", PlainConnectionSocketFactory.getSocketFactory())
                    .register("https", sslsf)
                    .build();
            return new PoolingHttpClientConnectionManager(registry);
        } catch (Exception e) {
            throw new RuntimeException("Failed to create trust-all SSL context", e);
        }
    }
}
