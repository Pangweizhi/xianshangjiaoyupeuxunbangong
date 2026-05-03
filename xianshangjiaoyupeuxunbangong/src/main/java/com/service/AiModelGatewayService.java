package com.service;

import java.util.List;
import java.util.Map;

public interface AiModelGatewayService {
    boolean isEnabled();
    String chat(List<Map<String, String>> messages);
}
