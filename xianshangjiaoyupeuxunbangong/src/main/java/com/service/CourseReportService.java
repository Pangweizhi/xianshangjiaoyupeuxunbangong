package com.service;

import java.util.Map;

public interface CourseReportService {
    Map<String, Object> buildOverview(String role, Integer userId);

    Map<String, Object> buildStudentSummary(Integer yonghuId);
}
