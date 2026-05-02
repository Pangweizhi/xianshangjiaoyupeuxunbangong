package com.controller;

import com.service.CourseCreditRecordService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/courseCreditRecord")
public class CourseCreditRecordController {

    @Autowired
    private CourseCreditRecordService courseCreditRecordService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        }
        CommonUtil.checkMap(params);
        PageUtils page = courseCreditRecordService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/myPage")
    public R myPage(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("yonghuId", request.getSession().getAttribute("userId"));
        CommonUtil.checkMap(params);
        return R.ok().put("data", courseCreditRecordService.queryPage(params));
    }
}
