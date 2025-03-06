'use client';
import { withAuth } from '../contexts/withAuth';

interface Course {
  id: number;
  name: string;
  account_id: number;
}

interface CourseList {
  courseList: Course[];
}

// utils/api.ts
export async function getCourseList() {
  const res = await fetch('http://localhost:8000/get-courses', {
    method: 'GET',
    credentials: 'include', // Ensure the HTTP‑only cookie is sent with the request.
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    throw new Error('Failed to fetch protected data');
  }

  const data = await res.json();
  const courseObjectArray = data as CourseList;
  return courseObjectArray;
}

export function CourseButton() {
  const courseList = getCourseList();
  if (courseList instanceof Array) {
    console.log('creating component');
    return (
      <div>
        {courseList.map((course: Course, index: number) => (
          <button
            key={index}
            className="w-full text-left py-2 px-4 rounded-lg bg-gray-100 text-blue-600 font-semibold"
          >
            {course.name}
          </button>
        ))}
      </div>
    );
  } else {
    console.log('component not created');
    console.log(courseList);
  }
}
export const Sidebar = () => {
  return (
    <div className="h-screen w-64 bg-white shadow-lg flex flex-col p-4">
      {/* Logo Section */}
      {/* <div className="mb-6 flex justify-center">
        <img src="" alt="Logo" className="h-10 w-10 bg-gray-200 rounded-full" />
      </div> */}

      {/* Navigation */}

      <nav className="flex flex-col space-y-2">
        <CourseButton />
      </nav>
    </div>
  );
};

export default withAuth(Sidebar);
