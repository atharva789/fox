import axios from 'axios';

interface Calendar {
  ics: string;
}
interface Course {
  id: number;
  name: string;
  account_id: number;
  calendar: Calendar;
}

const getCourseList = async (apiKey: string) => {
  //make request to canvasAPI using API Key
  const response = await fetch(
    'https://canvas.case.edu/api/v1/courses/?enrollment_state=active&include[]=term',
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${process.env.CANVAS_API_KEY}`,
        'Content-Type': 'application/json',
      },
    }
  );

  const data = await response.json;
  let courseObjectArray: Course[] = [];
  for (var item in data) {
    courseObjectArray.push(JSON.parse(item) as Course);
  }
  return courseObjectArray;
};

export function CourseButton() {
  const courseList = getCourseList('');
  if (courseList instanceof Array) {
    return (
      <>
        {courseList.map((course: Course, index: any) => (
          <button
            key={index}
            className="w-full text-left py-2 px-4 rounded-lg bg-gray-100 text-blue-600 font-semibold"
          >
            {course.name}
          </button>
        ))}
      </>
    );
  }
}
export default function Sidebar() {
  return (
    <div className="h-screen w-64 bg-white shadow-lg flex flex-col p-4">
      {/* Logo Section */}
      <div className="mb-6 flex justify-center">
        <img src="" alt="Logo" className="h-10 w-10 bg-gray-200 rounded-full" />
      </div>

      {/* Navigation */}

      <nav className="flex flex-col space-y-2">
        <CourseButton />
      </nav>
    </div>
  );
}
