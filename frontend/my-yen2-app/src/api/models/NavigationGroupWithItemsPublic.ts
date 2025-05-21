/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NavigationItemPublic } from './NavigationItemPublic';
export type NavigationGroupWithItemsPublic = {
    /**
     * 导航分组名称
     */
    name: string;
    /**
     * 导航分组描述 (可选)
     */
    description?: (string | null);
    /**
     * 排序索引，默认为0
     */
    order_index?: number;
    id: number;
    user_id: number;
    created_at: string;
    updated_at: string;
    items?: Array<NavigationItemPublic>;
};

