import * as React from "react"
import {
    IconCamera,
    IconChartBar,
    IconDashboard,
    IconFileAi,
    IconFileDescription,
    IconFolder,
    IconInnerShadowTop,
    IconListDetails, IconSearch,
    IconSettings,
    IconUsers,
} from "@tabler/icons-react"

import {NavMain} from "@/components/nav-main"
import {NavSecondary} from "@/components/nav-secondary"
import {NavUser} from "@/components/nav-user"
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"
import {Button} from "@/components/ui/button.tsx";

const data = {
    user: {
        name: "shadcn",
        email: "m@example.com",
        avatar: "/avatars/shadcn.jpg",
    },
    navMain: [
        {
            title: "Analytics",
            url: "",
            icon: IconChartBar,
        },
        {
            title: "Image Search",
            url: "../app/search/image-search.tsx",
            icon: IconSearch,
        }
    ],
    navClouds: [
        {
            title: "Capture",
            icon: IconCamera,
            isActive: true,
            url: "#",
            items: [
                {
                    title: "Active Proposals",
                    url: "#",
                },
                {
                    title: "Archived",
                    url: "#",
                },
            ],
        },
        {
            title: "Proposal",
            icon: IconFileDescription,
            url: "#",
            items: [
                {
                    title: "Active Proposals",
                    url: "#",
                },
                {
                    title: "Archived",
                    url: "#",
                },
            ],
        },
        {
            title: "Prompts",
            icon: IconFileAi,
            url: "#",
            items: [
                {
                    title: "Active Proposals",
                    url: "#",
                },
                {
                    title: "Archived",
                    url: "#",
                },
            ],
        },
    ],
    navSecondary: [
        {
            title: "Settings",
            url: "#",
            icon: IconSettings,
        },
    ],
}

export function AppSidebar({setActiveComponent, ...props}: {
    setActiveComponent: (component: string) => void;
} & React.ComponentProps<typeof Sidebar>) {
    return (
        <Sidebar collapsible="offcanvas" {...props}>
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton
                            asChild
                            className="data-[slot=sidebar-menu-button]:!p-1.5"
                        >
                            <a href="#">
                                <IconInnerShadowTop className="!size-5"/>
                                <span className="text-base font-semibold GOS">Intelligent-DMS</span>
                            </a>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>
            <SidebarContent>
                {/*<Button onClick={() => {*/}
                {/*    setActiveComponent("dashboard")*/}
                {/*}}>Dashboard</Button>*/}

                {/*<a href='../app/dashboard/dashboard.tsx'> <Button>Dashboard</Button></a>*/}
                {/*<a href='../app/search/image_search.tsx'> <Button>Image Search</Button></a>*/}
                <NavMain items={data.navMain} setActiveComponent={setActiveComponent}/>
                <NavSecondary items={data.navSecondary} className="mt-auto"/>
            </SidebarContent>
            <SidebarFooter>
                <NavUser user={data.user}/>
            </SidebarFooter>
        </Sidebar>
    );
}
