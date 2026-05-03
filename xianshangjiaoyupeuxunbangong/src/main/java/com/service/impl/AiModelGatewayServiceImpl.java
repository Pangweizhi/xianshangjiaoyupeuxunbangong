package com.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.service.AiModelGatewayService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service("aiModelGatewayService")
public class AiModelGatewayServiceImpl implements AiModelGatewayService {

    @Value("${qa.ai.enabled:false}")
    private boolean enabled;

    @Value("${qa.ai.api-key:}")
    private String apiKey;

    @Value("${qa.ai.base-url:}")
    private String baseUrl;

    @Value("${qa.ai.model:qwen-plus}")
    private String model;

    @Override
    public boolean isEnabled() {
        return enabled && StringUtils.isNotBlank(apiKey) && StringUtils.isNotBlank(baseUrl) && StringUtils.isNotBlank(model);
    }

    @Override
    public String chat(List<Map<String, String>> messages) {
        if (!isEnabled() || messages == null || messages.isEmpty()) {
            return null;
        }
        HttpURLConnection connection = null;
        try {
            URL url = new URL(normalizeBaseUrl(baseUrl) + "/chat/completions");
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(45000);
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Authorization", "Bearer " + apiKey);

            Map<String, Object> payload = new LinkedHashMap<String, Object>();
            payload.put("model", model);
            payload.put("temperature", 0.3D);
            payload.put("top_p", 0.9D);
            payload.put("messages", messages);

            byte[] requestBytes = JSON.toJSONString(payload).getBytes(StandardCharsets.UTF_8);
            DataOutputStream outputStream = new DataOutputStream(connection.getOutputStream());
            outputStream.write(requestBytes);
            outputStream.flush();
            outputStream.close();

            int status = connection.getResponseCode();
            String responseText = readAll(status >= 200 && status < 300 ? connection.getInputStream() : connection.getErrorStream());
            if (StringUtils.isBlank(responseText)) {
                return null;
            }
            JSONObject root = JSON.parseObject(responseText);
            JSONArray choices = root.getJSONArray("choices");
            if (choices == null || choices.isEmpty()) {
                return null;
            }
            JSONObject first = choices.getJSONObject(0);
            if (first == null) {
                return null;
            }
            JSONObject message = first.getJSONObject("message");
            return message == null ? null : message.getString("content");
        } catch (Exception e) {
            return null;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private String normalizeBaseUrl(String source) {
        String value = source.trim();
        if (value.endsWith("/")) {
            return value.substring(0, value.length() - 1);
        }
        return value;
    }

    private String readAll(InputStream inputStream) throws Exception {
        if (inputStream == null) {
            return null;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
        StringBuilder builder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            builder.append(line);
        }
        reader.close();
        return builder.toString();
    }
}
