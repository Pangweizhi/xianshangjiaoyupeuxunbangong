package com.controller;

import com.service.CourseReportService;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;

@RestController
@Controller
@RequestMapping("/courseReport")
public class CourseReportController {

    @Autowired
    private CourseReportService courseReportService;

    @RequestMapping("/overview")
    public R overview(HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        Object userIdValue = request.getSession().getAttribute("userId");
        Integer userId = userIdValue == null ? null : Integer.valueOf(String.valueOf(userIdValue));
        return R.ok().put("data", courseReportService.buildOverview(role, userId));
    }

    @RequestMapping("/mySummary")
    public R mySummary(HttpServletRequest request) {
        Object userIdValue = request.getSession().getAttribute("userId");
        Integer userId = userIdValue == null ? null : Integer.valueOf(String.valueOf(userIdValue));
        return R.ok().put("data", courseReportService.buildStudentSummary(userId));
    }
}
