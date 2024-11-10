from database.connect import Files, session

new_file = Files.create(session, file_name='test.txt')
print("Created:", new_file.destructure())

retrieved_file = Files.get_by_name(session, new_file.file_name)
print("Retrieved:", retrieved_file.destructure())

updated_file = Files.update_uploaded_status(session, retrieved_file.id, True)
print("Updated:", updated_file.destructure())

deleted_file = Files.delete(session, updated_file.id)
print("Deleted:", deleted_file.destructure())