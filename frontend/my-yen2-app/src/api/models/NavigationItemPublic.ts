/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type NavigationItemPublic = {
    /**
     * 导航项标题
     */
    title: string;
    /**
     * 导航项的有效链接 URL
     */
    url: string;
    /**
     * 导航项图标的 URL (可选)
     */
    icon_url?: (string | null);
    /**
     * 导航项描述 (可选)
     */
    description?: (string | null);
    /**
     * 组内排序索引，默认为0
     */
    order_index?: number;
    id: number;
    group_id: number;
    created_at: string;
    updated_at: string;
};

